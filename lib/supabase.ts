// lib/supabase.ts
import { createClient } from "@supabase/supabase-js";

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL!;
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!;

if (!supabaseUrl || !supabaseAnonKey) {
  throw new Error("Missing Supabase environment variables");
}

export const supabase = createClient(supabaseUrl, supabaseAnonKey);

// TypeScript 타입 정의 (기본)
export type Course = {
  id: string;
  title: string;
  instructor: string;
  url: string;
  price_krw: number | null;
  discount_price_krw: number | null;
  rating: number | null;
  student_count: number;
  category: string | null;
  subcategory: string | null;
  difficulty_level: string | null;
  duration_hours: number | null;
  is_trending: boolean;
  created_at: string;
  updated_at: string;
};
