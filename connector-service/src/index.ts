import Server from './server.js';
import logger from './logger.js';
import config from './config.js';

async function main(): Promise<void> {
  try {
    logger.info('Starting Telegram Expense Bot Connector Service...');
    logger.info(`Node.js version: ${process.version}`);
    logger.info(`Environment: ${config.server.nodeEnv}`);
    logger.info(`Port: ${config.server.port}`);

    // Create and start the server
    const server = new Server();
    await server.start();

    // Graceful shutdown handling
    const gracefulShutdown = (): void => {
      logger.info('Received shutdown signal, gracefully closing server...');
      server.stop();
      process.exit(0);
    };

    // Listen for termination signals
    process.on('SIGTERM', gracefulShutdown);
    process.on('SIGINT', gracefulShutdown);

    logger.info('Connector Service started successfully');

  } catch (error) {
    logger.error('Failed to start Connector Service:', error);
    process.exit(1);
  }
}

// Handle unhandled rejections and exceptions
process.on('unhandledRejection', (reason, promise) => {
  logger.error('Unhandled Rejection at:', promise, 'reason:', reason);
  process.exit(1);
});

process.on('uncaughtException', (error) => {
  logger.error('Uncaught Exception:', error);
  process.exit(1);
});

// Start the application
main().catch((error) => {
  logger.error('Error in main function:', error);
  process.exit(1);
}); 