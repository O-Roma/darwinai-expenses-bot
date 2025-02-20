import { Telegraf, Context } from "telegraf";
import { message } from "telegraf/filters";
import axios from "axios";
import dotenv from "dotenv";
import winston from "winston";

dotenv.config();

// Logger Setup
const logger = winston.createLogger({
  level: "info",
  format: winston.format.json(),
  transports: [
    new winston.transports.Console({ format: winston.format.simple() }),
    new winston.transports.File({ filename: "bot.log" }),
  ],
});

const BOT_TOKEN = process.env.TELEGRAM_BOT_TOKEN;
const BOT_SERVICE_URL = process.env.BOT_SERVICE_URL;

if (!BOT_TOKEN || !BOT_SERVICE_URL) {
  logger.error(
    "Missing required environment variables: TELEGRAM_BOT_TOKEN or BOT_SERVICE_URL"
  );
  process.exit(1);
}

const bot = new Telegraf(BOT_TOKEN);

bot.start((ctx) => {
  const userId = ctx.from?.id;
  const userName = ctx.from?.first_name || "User";

  logger.info(`User ${userId} started the bot`, { userId, userName });

  ctx.reply(
    `👋 *Welcome, ${userName}!* \n\nI can help you track your expenses. Just tell me what you spent and on what! 💰\n\n` +
      `📌 *Example:* \`Spent 50 on groceries\`\n\n` +
      `Type /help to see more options.`,
    { parse_mode: "Markdown" }
  );
});

bot.help((ctx) => {
  ctx.reply(
    `🆘 *How to Use Me* 🆘\n
I can help you track your expenses. Just send me a message with the amount and category.

📌 *Examples:*  
💰 \`Spent 20 on food\`  
🚕 \`Taxi 15\`  
🛍️ \`Bought groceries for 50\`
Give it a try!`,
    { parse_mode: "Markdown" }
  );
});

bot.on(message("text"), async (ctx: Context) => {
  const userId = ctx.from?.id;
  const userMessage = ctx.text || "";

  logger.info(`Received message from ${userId}: ${userMessage}`);

  try {
    const startTime = Date.now();
    const response = await axios.post(BOT_SERVICE_URL, {
      telegram_id: String(userId),
      message: userMessage,
    });
    const duration = Date.now() - startTime;

    const { status, message: responseMessage, data } = response.data;
    logger.info(`Response from service in ${duration}ms`, {
      status,
      responseMessage,
    });

    if (data?.category) {
      await ctx.reply(`${data.category} expense added ✅`);
    }
  } catch (error: unknown) {
    if (axios.isAxiosError(error)) {
      logger.error("Axios error", {
        message: error.message,
        response: error.response?.data,
      });
      await ctx.reply(
        "Error connecting to the service. Please try again later."
      );
    } else if (error instanceof Error) {
      logger.error("Error processing message", {
        message: error.message,
        stack: error.stack,
      });
    } else {
      logger.error("An unknown error occurred", { error: String(error) });
    }
    await ctx.reply("An error occurred while processing your request.");
  }
});

bot.launch().then(() => {
  logger.info("Telegram bot started...");
});

process.once("SIGINT", () => {
  logger.warn("Bot stopping (SIGINT)");
  bot.stop("SIGINT");
});
process.once("SIGTERM", () => {
  logger.warn("Bot stopping (SIGTERM)");
  bot.stop("SIGTERM");
});
