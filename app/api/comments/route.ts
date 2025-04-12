import { NextResponse } from "next/server"
import { supabase } from "@/lib/supabase"

export async function POST(request: Request) {
    try {
        const { meme_id, parent_id, content, author } = await request.json()

        // Insert the new comment into the database
        const { error: insertError } = await supabase.from("comments").insert([
            {
                meme_id,
                parent_id,
                content,
                author,
            },
        ])

        if (insertError) {
            console.error("Error inserting comment:", insertError)
            return NextResponse.json(
                { error: "Failed to create comment" },
                { status: 500 }
            )
        }

        return NextResponse.json({ success: true })
    } catch (error) {
        console.error("Error in comments API route:", error)
        return NextResponse.json(
            { error: "Internal server error" },
            { status: 500 }
        )
    }
} 