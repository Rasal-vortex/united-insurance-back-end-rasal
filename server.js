import "dotenv/config";
import app from "./src/app.js";
import { prisma } from "./src/config/prisma.js";
import os from "os";

const configuredPort = Number(process.env.PORT || 3000);

if (
  !Number.isInteger(configuredPort) ||
  configuredPort < 0 ||
  configuredPort > 65535
) {
  throw new Error("PORT must be an integer between 0 and 65535");
}

const getLocalIP = () => {
  const interfaces = os.networkInterfaces();
  for (const nets of Object.values(interfaces)) {
    for (const net of nets) {
      if (net.family === "IPv4" && !net.internal) {
        return net.address;
      }
    }
  }
  return "localhost";
};

function listenOnAvailablePort(port) {
  return new Promise((resolve, reject) => {
    const server = app.listen(port);

    server.once("listening", () => resolve(server));
    server.once("error", (error) => {
      if (error.code === "EADDRINUSE" && port > 0 && port < 65535) {
        console.warn(`Port ${port} is already in use; trying ${port + 1}`);
        listenOnAvailablePort(port + 1).then(resolve, reject);
        return;
      }

      reject(error);
    });
  });
}

const serverPromise = listenOnAvailablePort(configuredPort);

serverPromise.then((server) => {
  const port = server.address().port;
  const ip = getLocalIP();
  console.log(`  Local:   http://localhost:${port}`);
  console.log(`  Network: http://${ip}:${port}`);

  async function shutdown(signal) {
    console.info(`${signal} received; shutting down`);
    server.close(async () => {
      await prisma.$disconnect();
      process.exit(0);
    });
  }

  process.on("SIGINT", () => shutdown("SIGINT"));
  process.on("SIGTERM", () => shutdown("SIGTERM"));
});

serverPromise.catch((error) => {
  console.error("Failed to start server:", error);
  process.exitCode = 1;
});
