import { NextResponse } from "next/server"
import { supabase } from "@/lib/supabase"
import { auth } from "@clerk/nextjs/server"

export async function PATCH(request: Request) {
    try {
        const { userId } = await auth()
        if (!userId) {
            return NextResponse.json(
                { error: "Unauthorized" },
                { status: 401 }
            )
        }

        const { newUsername } = await request.json()

        // Update all memes and comments with the new username
        const { error: memesError } = await supabase
            .from("memes")
            .update({ author: newUsername })
            .eq("author", userId)

        if (memesError) {
            console.error("Error updating memes:", memesError)
            return NextResponse.json(
                { error: "Failed to update username in memes" },
                { status: 500 }
            )
        }

        const { error: commentsError } = await supabase
            .from("comments")
            .update({ author: newUsername })
            .eq("author", userId)

        if (commentsError) {
            console.error("Error updating comments:", commentsError)
            return NextResponse.json(
                { error: "Failed to update username in comments" },
                { status: 500 }
            )
        }

        return NextResponse.json({ success: true })
    } catch (error) {
        console.error("Error in users API route:", error)
        return NextResponse.json(
            { error: "Internal server error" },
            { status: 500 }
        )
    }
} 
