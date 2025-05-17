import express from 'express';
import cors from 'cors';
import { createClient } from 'redis';
import { v4 as uuidv4 } from 'uuid';
import axios from 'axios';
import dotenv from 'dotenv';

dotenv.config();

const app = express();
const port = process.env.PORT || 3001;
const redis = createClient({ url: process.env.REDIS_URL });
redis.on('error', err => console.error('Redis Client Error', err));
await redis.connect();
const RAG_API_URL = process.env.RAG_API_URL || 'http://localhost:8000/query';   

app.use(cors());
app.use(express.json());

app.post('/session', async (req, res) => {
  const sessionId = uuidv4();
  await redis.del(`session:${sessionId}`);
  await redis.expire(`session:${sessionId}`, 3600);
  res.json({ sessionId });
});

app.post('/query', async (req, res) => {
  const { sessionId, query } = req.body;
  if (!sessionId || !query) {
    return res.status(400).json({ error: 'sessionId and query are required' });
  }
  try {
    await redis.rPush(`session:${sessionId}`, JSON.stringify({ role: 'user', content: query }));
    const ragRes = await axios.post(RAG_API_URL, { query });
    const botReply = ragRes.data.answer || ragRes.data.result || ragRes.data.response;
    await redis.rPush(`session:${sessionId}`, JSON.stringify({ role: 'bot', content: botReply }));
    await redis.expire(`session:${sessionId}`, 3600);
    res.json({ response: botReply });
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: 'Failed to get response', details: err.message });
  }
});

app.get('/session/:sessionId/history', async (req, res) => {
  const { sessionId } = req.params;
  try {
    const messages = await redis.lRange(`session:${sessionId}`, 0, -1);
    const history = messages.map(msg => JSON.parse(msg));
    res.json({ history });
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: 'Failed to fetch history', details: err.message });
  }
});

app.delete('/session/:sessionId', async (req, res) => {
  const { sessionId } = req.params;
  try {
    await redis.del(`session:${sessionId}`);
    res.json({ message: 'Session history cleared.' });
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: 'Failed to clear session', details: err.message });
  }
});

app.listen(port, () => {
  console.log(`Node API server listening on http://localhost:${port}`);
});