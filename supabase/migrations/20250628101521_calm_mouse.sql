/*
  # Initial ClipVault Database Schema

  1. New Tables
    - `users`
      - `id` (uuid, primary key)
      - `email` (text, unique)
      - `name` (text)
      - `role` (text)
      - `organization` (text)
      - `created_at` (timestamp)
      - `updated_at` (timestamp)
    
    - `devices`
      - `id` (uuid, primary key)
      - `user_id` (uuid, foreign key)
      - `name` (text)
      - `type` (text)
      - `platform` (text)
      - `ip_address` (text)
      - `trusted` (boolean)
      - `status` (text)
      - `last_seen` (timestamp)
      - `fingerprint` (text)
      - `created_at` (timestamp)
      - `updated_at` (timestamp)
    
    - `clipboard_items`
      - `id` (uuid, primary key)
      - `user_id` (uuid, foreign key)
      - `device_id` (uuid, foreign key)
      - `content` (text, encrypted)
      - `content_type` (text)
      - `domain` (text)
      - `hash` (text)
      - `iv` (text)
      - `created_at` (timestamp)
      - `expires_at` (timestamp)
    
    - `security_events`
      - `id` (uuid, primary key)
      - `user_id` (uuid, foreign key)
      - `event_type` (text)
      - `severity` (text)
      - `description` (text)
      - `source` (text)
      - `ip_address` (text)
      - `user_agent` (text)
      - `blocked` (boolean)
      - `details` (jsonb)
      - `created_at` (timestamp)
    
    - `security_policies`
      - `id` (uuid, primary key)
      - `user_id` (uuid, foreign key)
      - `policy_data` (jsonb)
      - `created_at` (timestamp)
      - `updated_at` (timestamp)
    
    - `domain_whitelist`
      - `id` (uuid, primary key)
      - `user_id` (uuid, foreign key)
      - `domain` (text)
      - `created_at` (timestamp)

  2. Security
    - Enable RLS on all tables
    - Add policies for authenticated users to access their own data
    - Add policies for device management
    - Add policies for clipboard synchronization
*/

-- Create users table (extends Supabase auth.users)
CREATE TABLE IF NOT EXISTS users (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  auth_id uuid REFERENCES auth.users(id) ON DELETE CASCADE,
  email text UNIQUE NOT NULL,
  name text NOT NULL,
  role text DEFAULT 'user' CHECK (role IN ('admin', 'user')),
  organization text DEFAULT '',
  created_at timestamptz DEFAULT now(),
  updated_at timestamptz DEFAULT now()
);

-- Create devices table
CREATE TABLE IF NOT EXISTS devices (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id uuid REFERENCES users(id) ON DELETE CASCADE NOT NULL,
  name text NOT NULL,
  type text DEFAULT 'desktop' CHECK (type IN ('desktop', 'laptop', 'mobile', 'tablet')),
  platform text NOT NULL,
  ip_address text,
  trusted boolean DEFAULT false,
  status text DEFAULT 'offline' CHECK (status IN ('online', 'offline')),
  last_seen timestamptz DEFAULT now(),
  fingerprint text UNIQUE,
  created_at timestamptz DEFAULT now(),
  updated_at timestamptz DEFAULT now()
);

-- Create clipboard_items table
CREATE TABLE IF NOT EXISTS clipboard_items (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id uuid REFERENCES users(id) ON DELETE CASCADE NOT NULL,
  device_id uuid REFERENCES devices(id) ON DELETE CASCADE NOT NULL,
  content text NOT NULL, -- encrypted content
  content_type text DEFAULT 'text' CHECK (content_type IN ('text', 'password', 'code')),
  domain text NOT NULL,
  hash text NOT NULL,
  iv text NOT NULL,
  created_at timestamptz DEFAULT now(),
  expires_at timestamptz DEFAULT (now() + interval '30 days')
);

-- Create security_events table
CREATE TABLE IF NOT EXISTS security_events (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id uuid REFERENCES users(id) ON DELETE CASCADE,
  event_type text NOT NULL CHECK (event_type IN ('authentication', 'encryption', 'access_control', 'threat_detection', 'policy_violation')),
  severity text DEFAULT 'low' CHECK (severity IN ('low', 'medium', 'high', 'critical')),
  description text NOT NULL,
  source text NOT NULL,
  ip_address text,
  user_agent text,
  blocked boolean DEFAULT false,
  details jsonb DEFAULT '{}',
  created_at timestamptz DEFAULT now()
);

-- Create security_policies table
CREATE TABLE IF NOT EXISTS security_policies (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id uuid REFERENCES users(id) ON DELETE CASCADE NOT NULL,
  policy_data jsonb NOT NULL DEFAULT '{}',
  created_at timestamptz DEFAULT now(),
  updated_at timestamptz DEFAULT now(),
  UNIQUE(user_id)
);

-- Create domain_whitelist table
CREATE TABLE IF NOT EXISTS domain_whitelist (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id uuid REFERENCES users(id) ON DELETE CASCADE NOT NULL,
  domain text NOT NULL,
  created_at timestamptz DEFAULT now(),
  UNIQUE(user_id, domain)
);

-- Enable Row Level Security
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE devices ENABLE ROW LEVEL SECURITY;
ALTER TABLE clipboard_items ENABLE ROW LEVEL SECURITY;
ALTER TABLE security_events ENABLE ROW LEVEL SECURITY;
ALTER TABLE security_policies ENABLE ROW LEVEL SECURITY;
ALTER TABLE domain_whitelist ENABLE ROW LEVEL SECURITY;

-- Create policies for users table
CREATE POLICY "Users can read own data"
  ON users
  FOR SELECT
  TO authenticated
  USING (auth.uid() = auth_id);

CREATE POLICY "Users can update own data"
  ON users
  FOR UPDATE
  TO authenticated
  USING (auth.uid() = auth_id);

CREATE POLICY "Users can insert own data"
  ON users
  FOR INSERT
  TO authenticated
  WITH CHECK (auth.uid() = auth_id);

-- Create policies for devices table
CREATE POLICY "Users can manage own devices"
  ON devices
  FOR ALL
  TO authenticated
  USING (user_id IN (SELECT id FROM users WHERE auth_id = auth.uid()));

-- Create policies for clipboard_items table
CREATE POLICY "Users can manage own clipboard items"
  ON clipboard_items
  FOR ALL
  TO authenticated
  USING (user_id IN (SELECT id FROM users WHERE auth_id = auth.uid()));

-- Create policies for security_events table
CREATE POLICY "Users can read own security events"
  ON security_events
  FOR SELECT
  TO authenticated
  USING (user_id IN (SELECT id FROM users WHERE auth_id = auth.uid()) OR user_id IS NULL);

CREATE POLICY "Users can insert security events"
  ON security_events
  FOR INSERT
  TO authenticated
  WITH CHECK (user_id IN (SELECT id FROM users WHERE auth_id = auth.uid()) OR user_id IS NULL);

-- Create policies for security_policies table
CREATE POLICY "Users can manage own security policies"
  ON security_policies
  FOR ALL
  TO authenticated
  USING (user_id IN (SELECT id FROM users WHERE auth_id = auth.uid()));

-- Create policies for domain_whitelist table
CREATE POLICY "Users can manage own domain whitelist"
  ON domain_whitelist
  FOR ALL
  TO authenticated
  USING (user_id IN (SELECT id FROM users WHERE auth_id = auth.uid()));

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_devices_user_id ON devices(user_id);
CREATE INDEX IF NOT EXISTS idx_devices_fingerprint ON devices(fingerprint);
CREATE INDEX IF NOT EXISTS idx_clipboard_items_user_id ON clipboard_items(user_id);
CREATE INDEX IF NOT EXISTS idx_clipboard_items_device_id ON clipboard_items(device_id);
CREATE INDEX IF NOT EXISTS idx_clipboard_items_created_at ON clipboard_items(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_security_events_user_id ON security_events(user_id);
CREATE INDEX IF NOT EXISTS idx_security_events_created_at ON security_events(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_security_events_severity ON security_events(severity);
CREATE INDEX IF NOT EXISTS idx_domain_whitelist_user_id ON domain_whitelist(user_id);

-- Create function to automatically update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = now();
  RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers for updated_at
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_devices_updated_at BEFORE UPDATE ON devices
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_security_policies_updated_at BEFORE UPDATE ON security_policies
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Create function to clean up expired clipboard items
CREATE OR REPLACE FUNCTION cleanup_expired_clipboard_items()
RETURNS void AS $$
BEGIN
  DELETE FROM clipboard_items WHERE expires_at < now();
END;
$$ language 'plpgsql';

-- Create function to get user by auth_id
CREATE OR REPLACE FUNCTION get_user_by_auth_id(auth_user_id uuid)
RETURNS TABLE(
  id uuid,
  email text,
  name text,
  role text,
  organization text,
  created_at timestamptz,
  updated_at timestamptz
) AS $$
BEGIN
  RETURN QUERY
  SELECT u.id, u.email, u.name, u.role, u.organization, u.created_at, u.updated_at
  FROM users u
  WHERE u.auth_id = auth_user_id;
END;
$$ language 'plpgsql' SECURITY DEFINER;