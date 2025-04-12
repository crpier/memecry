"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Textarea } from "@/components/ui/textarea"
import { Loader2 } from "lucide-react"
import { useUser } from "@clerk/nextjs"

interface CommentFormProps {
  memeId: string
  parentId?: string | null
  onCommentAddedAction: () => void
  isReply?: boolean
}

export function CommentForm({ memeId, parentId = null, onCommentAddedAction, isReply = false }: CommentFormProps) {
  const [content, setContent] = useState("")
  const [error, setError] = useState("")
  const [isSubmitting, setIsSubmitting] = useState(false)
  const { user } = useUser()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsSubmitting(true)
    setError("")

    try {
      const response = await fetch("/api/comments", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          meme_id: memeId,
          parent_id: parentId,
          content,
          author: user?.username || user?.firstName || "Anonymous",
        }),
      })

      if (!response.ok) {
        throw new Error("Failed to post comment")
      }

      setContent("")
      onCommentAddedAction()
    } catch (err) {
      console.log(err)
      setError("Failed to post comment. Please try again.")
    } finally {
      setIsSubmitting(false)
    }
  }

  if (!user) return null

  return (
    <form onSubmit={handleSubmit} className="space-y-3 mt-4">
      <div>
        <Textarea
          placeholder={isReply ? "Write a reply..." : "Write a comment..."}
          value={content}
          onChange={(e) => setContent(e.target.value)}
          className="w-full min-h-[80px] bg-background dark:bg-background"
          disabled={isSubmitting}
        />
      </div>
      {error && <p className="text-sm text-destructive">{error}</p>}
      <div className="flex justify-end">
        <Button type="submit" size="sm" disabled={isSubmitting} className="primary-button">
          {isSubmitting ? (
            <>
              <Loader2 className="h-4 w-4 animate-spin mr-2" />
              {isReply ? "Posting Reply..." : "Posting Comment..."}
            </>
          ) : isReply ? (
            "Post Reply"
          ) : (
            "Post Comment"
          )}
        </Button>
      </div>
    </form>
  )
}
