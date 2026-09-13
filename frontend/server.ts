import express from "express";
import cors from "cors";
import multer from "multer";
import { GoogleGenAI } from "@google/genai";
import path from "path";
import fs from "fs";
import { fileURLToPath } from "url";
import { dirname } from "path";
import { createServer as createViteServer } from "vite";

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

const ai = new GoogleGenAI({ apiKey: process.env.GEMINI_API_KEY });
const upload = multer({ dest: "uploads/" });

async function startServer() {
  const app = express();
  const PORT = 3000;

  app.use(cors());
  app.use(express.json());

  // Ensure uploads directory exists
  if (!fs.existsSync("uploads")) {
    fs.mkdirSync("uploads");
  }

  app.post("/api/upload", upload.single("file"), async (req, res) => {
    try {
      const file = req.file;
      if (!file) {
        return res.status(400).json({ error: "No file uploaded" });
      }

      console.log(`Uploading file ${file.originalname} to Gemini...`);
      const uploadResult = await ai.files.upload({
        file: file.path,
        mimeType: file.mimetype || "application/pdf",
      });

      // Cleanup local temp file
      fs.unlinkSync(file.path);

      res.json({
        status: "success",
        collection_name: uploadResult.name, // Use Gemini file ID as collection_name
        filename: file.originalname,
      });
    } catch (error: any) {
      console.error("Upload error:", error);
      res.status(500).json({ error: error.message });
    }
  });

  app.post("/api/chat", async (req, res) => {
    try {
      const { collection_name, question, history } = req.body;
      if (!collection_name || !question) {
        return res.status(400).json({ error: "Missing required fields" });
      }

      // Convert frontend history to Gemini format (user/model)
      const contents = history.map((msg: any) => ({
        role: msg.role === "assistant" ? "model" : "user",
        parts: [{ text: msg.content }],
      }));

      // Add the file context to the VERY FIRST message, or as system instruction
      // Using system instructions is cleaner
      const fileContext = await ai.files.get({ name: collection_name });

      // Add current question along with the file context
      contents.push({
        role: "user",
        parts: [
          { fileData: { fileUri: fileContext.uri, mimeType: fileContext.mimeType } },
          { text: question }
        ],
      });

      const response = await ai.models.generateContent({
        model: "gemini-2.5-pro",
        contents,
        config: {
          systemInstruction: "You are a Research Paper Agent. Base your answers on the provided document.",
        }
      });

      res.json({
        answer: response.text,
        citations: [],
        collection_name,
        messages: [...history, { role: "user", content: question }, { role: "assistant", content: response.text }],
      });
    } catch (error: any) {
      console.error("Chat error:", error);
      res.status(500).json({ error: error.message });
    }
  });

  if (process.env.NODE_ENV !== "production") {
    const vite = await createViteServer({
      server: { middlewareMode: true },
      appType: "spa",
    });
    app.use(vite.middlewares);
  } else {
    const distPath = path.join(process.cwd(), "dist");
    app.use(express.static(distPath));
    app.get("*", (req, res) => {
      res.sendFile(path.join(distPath, "index.html"));
    });
  }

  app.listen(PORT, "0.0.0.0", () => {
    console.log(`Server running on port ${PORT}`);
  });
}

startServer();
