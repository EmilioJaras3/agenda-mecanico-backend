import { Injectable, Logger } from '@nestjs/common';
import { ConfigService } from '@nestjs/config';
import axios from 'axios';

@Injectable()
export class NotificationsService {
  private readonly logger = new Logger(NotificationsService.name);
  private webhookUrl: string;

  constructor(private configService: ConfigService) {
    this.webhookUrl = this.configService.get<string>('DISCORD_WEBHOOK_URL');
  }

  async sendDiscordNotification(title: string, message: string, color: number = 0x00ff00) {
    if (!this.webhookUrl || this.webhookUrl.includes('PLACEHOLDER')) {
      this.logger.warn('Discord Webhook URL no configurada. Saltando notificación.');
      return;
    }

    try {
      await axios.post(this.webhookUrl, {
        embeds: [{
          title: `🛠️ APEX FORGE - ${title}`,
          description: message,
          color: color,
          timestamp: new Date().toISOString(),
          footer: { text: 'Sistema de Notificaciones Automáticas' }
        }]
      });
      this.logger.log(`Notificación enviada: ${title}`);
    } catch (error) {
      this.logger.error('Error enviando notificación a Discord', error.message);
    }
  }
}
