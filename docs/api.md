# API Documentation

The backend API uses FastAPI OpenAPI standard. Live Swagger documentation is available at `http://localhost:8000/docs`.

## Endpoint Summary

### Authentication
- `POST /api/auth/register` - Create user account and issue JWT token.
- `POST /api/auth/login` - Authenticate credentials and return JWT bearer token.
- `POST /api/auth/logout` - Logout user.
- `GET /api/auth/me` - Fetch profile details of currently authenticated user.

### Templates
- `GET /api/templates` - List all email body templates.
- `POST /api/templates` - Create a new email template with subject and body tags.
- `GET /api/templates/{id}` - Get template details.
- `PUT /api/templates/{id}` - Update template.
- `DELETE /api/templates/{id}` - Delete template.
- `POST /api/templates/{id}/duplicate` - Clone an existing template.
- `POST /api/templates/preview` - Render template with dynamic sample values.

### Recipients & CSV
- `POST /api/recipients/upload` - Upload and analyze CSV file. Returns total, valid, invalid, duplicate rows and column detection.
- `POST /api/recipients/import` - Bulk import valid CSV recipients to database.
- `GET /api/recipients` - Query stored database recipients with search and pagination.
- `POST /api/recipients` - Add single recipient manually.
- `DELETE /api/recipients/{id}` - Remove recipient.
- `GET /api/recipients/groups/list` - List recipient groups.

### Campaigns
- `GET /api/campaigns` - List all campaigns.
- `POST /api/campaigns` - Create a new campaign (supports optional attachment upload).
- `GET /api/campaigns/{id}` - Get campaign status.
- `POST /api/campaigns/{id}/send` - Asynchronously launch email campaign.
- `POST /api/campaigns/{id}/cancel` - Safely halt pending emails for active campaign.
- `GET /api/campaigns/{id}/progress` - Fetch real-time sending metrics (percentage, sent, failed, cancelled, pending).
- `GET /api/campaigns/{id}/recipients` - Detailed delivery status per recipient.

### Settings & Health
- `GET /api/settings` - Get SMTP configuration (password masked).
- `POST /api/settings` - Update SMTP settings.
- `POST /api/settings/test-smtp` - Live test SMTP connection.
- `GET /api/dashboard/stats` - Summary statistics for dashboard cards and charts.
- `GET /health` - System, database, and Redis queue health status.

