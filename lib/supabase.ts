import { createClient } from "@supabase/supabase-js"

if (!process.env.NEXT_PUBLIC_SUPABASE_URL) {
  throw new Error('Missing env.NEXT_PUBLIC_SUPABASE_URL')
}
if (!process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY) {
  throw new Error('Missing env.NEXT_PUBLIC_SUPABASE_ANON_KEY')
}

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY

// Create a single supabase client for the entire app
export const supabase = createClient(supabaseUrl, supabaseAnonKey)

export type DbMeme = {
  id: string
  title: string
  image_url: string
  author: string
  created_at: string
  likes: number
  dislikes: number
  tag: string
}

export type DbComment = {
  id: string
  meme_id: string
  author: string
  content: string
  created_at: string
  parent_id: string | null
}
