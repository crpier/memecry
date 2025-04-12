import { NextResponse } from "next/server"
import { supabase } from "@/lib/supabase"

export async function POST(request: Request) {
    try {
        const { title, image_url, author, tag } = await request.json()

        // Insert the new meme into the database
        const { error: insertError } = await supabase.from("memes").insert([
            {
                title,
                image_url,
                author,
                tag: tag || "Misc",
                likes: 0,
                dislikes: 0,
            },
        ])

        if (insertError) {
            console.error("Error inserting meme:", insertError)
            return NextResponse.json(
                { error: "Failed to create meme" },
                { status: 500 }
            )
        }

        return NextResponse.json({ success: true })
    } catch (error) {
        console.error("Error in memes API route:", error)
        return NextResponse.json(
            { error: "Internal server error" },
            { status: 500 }
        )
    }
} 