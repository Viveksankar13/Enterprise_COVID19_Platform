-- ==============================================================================
-- FILE: roles.sql (seed)
-- Enterprise COVID-19 Analytics Platform — RBAC Seed Data
-- ==============================================================================

-- ── Roles ────────────────────────────────────────────────────────────────────
INSERT INTO roles (name, description) VALUES
    ('admin',    'Full platform access. Manage users, trigger ETL, view all data.'),
    ('analyst',  'Read all dashboards, run SQL explorer queries, export data.'),
    ('viewer',   'Read-only dashboard access. Cannot export or run custom queries.'),
    ('api_user', 'Programmatic API access via API key. Rate-limited.')
ON CONFLICT (name) DO NOTHING;

-- ── Permissions ──────────────────────────────────────────────────────────────
-- admin: full access
INSERT INTO permissions (role_id, resource, action)
SELECT r.role_id, res.resource, act.action
FROM roles r
CROSS JOIN (VALUES
    ('analytics'),('countries'),('vaccinations'),('testing'),
    ('hospitalizations'),('kpis'),('etl'),('users'),('admin'),
    ('powerbi'),('audit_logs')
) AS res(resource)
CROSS JOIN (VALUES ('read'),('write'),('execute'),('delete')) AS act(action)
WHERE r.name = 'admin'
ON CONFLICT (role_id, resource, action) DO NOTHING;

-- analyst: read + execute (no write/delete on users/admin)
INSERT INTO permissions (role_id, resource, action)
SELECT r.role_id, res.resource, act.action
FROM roles r
CROSS JOIN (VALUES
    ('analytics'),('countries'),('vaccinations'),('testing'),
    ('hospitalizations'),('kpis'),('powerbi')
) AS res(resource)
CROSS JOIN (VALUES ('read'),('execute')) AS act(action)
WHERE r.name = 'analyst'
ON CONFLICT (role_id, resource, action) DO NOTHING;

-- viewer: read only
INSERT INTO permissions (role_id, resource, action)
SELECT r.role_id, res.resource, 'read'
FROM roles r
CROSS JOIN (VALUES
    ('analytics'),('countries'),('vaccinations'),('testing'),
    ('hospitalizations'),('kpis'),('powerbi')
) AS res(resource)
WHERE r.name = 'viewer'
ON CONFLICT (role_id, resource, action) DO NOTHING;

-- api_user: read analytics and countries only
INSERT INTO permissions (role_id, resource, action)
SELECT r.role_id, res.resource, 'read'
FROM roles r
CROSS JOIN (VALUES ('analytics'),('countries'),('kpis')) AS res(resource)
WHERE r.name = 'api_user'
ON CONFLICT (role_id, resource, action) DO NOTHING;

-- ── Initial Admin User ───────────────────────────────────────────────────────
-- Password: Admin123! (bcrypt hash — CHANGE ON FIRST LOGIN)
INSERT INTO users (
    email, username, full_name, password_hash, role_id, is_active, is_verified
)
SELECT
    'admin@covid19analytics.local',
    'admin',
    'Platform Administrator',
    '$2b$12$1TzbTNzezbuPhAA2Nc.DmOg6CFwgY6xCzuJQZKMfMYF/41rRFex66',  -- admin
    r.role_id,
    TRUE,
    TRUE
FROM roles r WHERE r.name = 'admin'
ON CONFLICT (email) DO NOTHING;

-- ── Metadata Entries ─────────────────────────────────────────────────────────
INSERT INTO metadata (key, value, description) VALUES
    ('platform_version',      '1.0.0',           'Current platform version'),
    ('schema_version',        '1.0.0',           'Database schema version'),
    ('owid_dataset_url',      'https://covid.ourworldindata.org/data/owid-covid-data.csv',
                                                  'OWID COVID-19 dataset URL'),
    ('etl_schedule',          '0 6 * * *',       'Airflow ETL cron schedule (UTC)'),
    ('last_etl_run',          'NEVER',            'Timestamp of last successful ETL run'),
    ('last_matview_refresh',  'NEVER',            'Timestamp of last materialized view refresh'),
    ('maintenance_mode',      'false',            'When true, API returns 503 for non-admin users')
ON CONFLICT (key) DO NOTHING;

-- ── Verify ───────────────────────────────────────────────────────────────────
SELECT r.name AS role, COUNT(p.permission_id) AS permissions_count
FROM roles r
LEFT JOIN permissions p ON r.role_id = p.role_id
GROUP BY r.name
ORDER BY r.name;
