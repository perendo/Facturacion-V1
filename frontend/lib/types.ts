export interface User {
  id: number;
  email: string;
  full_name: string | null;
  created_at: string;
}

export interface Client {
  id: number;
  user_id: number;
  name: string;
  email: string | null;
  phone: string | null;
  address: string | null;
  tax_id: string | null;
  notes: string | null;
  created_at: string;
  updated_at: string;
}

export interface Product {
  id: number;
  user_id: number;
  name: string;
  description: string | null;
  unit_price: number;
  tax_rate: number;
  unit: string | null;
  created_at: string;
  updated_at: string;
}

export interface InvoiceLine {
  id: number;
  invoice_id: number;
  product_id: number | null;
  description: string;
  quantity: number;
  unit_price: number;
  discount: number;
  tax_rate: number;
  line_subtotal: number;
  line_tax: number;
  line_total: number;
}

export interface InvoiceLineCreate {
  product_id?: number | null;
  description: string;
  quantity: number;
  unit_price: number;
  discount: number;
  tax_rate: number;
}

export interface Invoice {
  id: number;
  user_id: number;
  client_id: number | null;
  series: string;
  year: number;
  sequence_number: number;
  number: string;
  issue_date: string;
  due_date: string | null;
  status: string;
  invoice_type: string;
  rectifies_invoice_id: number | null;
  rectification_reason: string | null;
  irpf_rate: number;
  irpf_total: number;
  global_discount: number;
  subtotal: number;
  tax_total: number;
  total: number;
  notes: string | null;
  created_at: string;
  updated_at: string;
  lines: InvoiceLine[];
}

export interface CompanyProfile {
  id: number;
  user_id: number;
  legal_name: string;
  tax_id: string;
  tax_address: string;
  postal_code: string;
  city: string;
  province: string;
  country: string;
  created_at: string;
  updated_at: string;
}

export interface CompanyProfileCreate {
  legal_name: string;
  tax_id: string;
  tax_address: string;
  postal_code: string;
  city: string;
  province: string;
  country?: string;
}

export interface DashboardSummary {
  total_invoiced: number;
  total_paid: number;
  total_pending: number;
  count_by_status: Record<string, number>;
}

export interface ApiErrorShape {
  detail?: string | unknown;
}