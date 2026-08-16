create extension if not exists pgcrypto;

create table if not exists admins (
  id uuid primary key default gen_random_uuid(),
  email text unique not null,
  password_hash text not null,
  created_at timestamptz not null default now()
);

create table if not exists customers (
  id uuid primary key default gen_random_uuid(),
  name text not null,
  phone text unique not null,
  email text,
  address text,
  lat numeric,
  lng numeric,
  referral_code text unique,
  wallet_balance numeric(12,2) not null default 0,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists products (
  id uuid primary key default gen_random_uuid(),
  name text not null,
  slug text unique not null,
  category text not null default 'essentials',
  description text,
  image_url text,
  price numeric(12,2) not null default 0,
  stock integer not null default 0,
  active boolean not null default true,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists orders (
  id uuid primary key default gen_random_uuid(),
  order_number text unique not null,
  customer_id uuid references customers(id),
  status text not null default 'new',
  payment_status text not null default 'pending',
  payment_method text not null default 'cod',
  razorpay_order_id text,
  razorpay_payment_id text,
  subtotal numeric(12,2) not null default 0,
  delivery_fee numeric(12,2) not null default 0,
  wallet_discount numeric(12,2) not null default 0,
  total numeric(12,2) not null default 0,
  delivery_address text,
  lat numeric,
  lng numeric,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists order_items (
  id uuid primary key default gen_random_uuid(),
  order_id uuid not null references orders(id) on delete cascade,
  product_id uuid references products(id),
  product_name text not null,
  unit_price numeric(12,2) not null,
  quantity integer not null check(quantity > 0),
  line_total numeric(12,2) not null
);

create table if not exists wallet_transactions (
  id uuid primary key default gen_random_uuid(),
  customer_id uuid not null references customers(id) on delete cascade,
  type text not null check(type in ('credit','debit')),
  amount numeric(12,2) not null,
  reason text not null,
  reference text,
  created_at timestamptz not null default now()
);

create table if not exists referrals (
  id uuid primary key default gen_random_uuid(),
  referrer_customer_id uuid not null references customers(id),
  referred_customer_id uuid references customers(id),
  referral_code text not null,
  reward_amount numeric(12,2) not null default 0,
  status text not null default 'pending',
  created_at timestamptz not null default now()
);

create table if not exists crm_notes (
  id uuid primary key default gen_random_uuid(),
  customer_id uuid not null references customers(id) on delete cascade,
  note text not null,
  next_follow_up timestamptz,
  created_at timestamptz not null default now()
);

create index if not exists idx_orders_customer on orders(customer_id);
create index if not exists idx_orders_created on orders(created_at desc);
create index if not exists idx_wallet_customer on wallet_transactions(customer_id);
create index if not exists idx_referrals_referrer on referrals(referrer_customer_id);
create index if not exists idx_crm_customer on crm_notes(customer_id);
