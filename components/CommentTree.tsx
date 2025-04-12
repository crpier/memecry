"use client"

import { useState, useEffect } from "react"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { Button } from "@/components/ui/button"
import { Reply } from "lucide-react"
import { CommentForm } from "./CommentForm"
import type { DbComment } from "@/lib/supabase"

type CommentWithReplies = DbComment & {
  replies?: CommentWithReplies[]
}

interface CommentTreeProps {
  comments: DbComment[]
  memeId: string
  onCommentAdded: () => void
}

const CommentItem = ({
  comment,
  memeId,
  onCommentAdded,
}: {
  comment: CommentWithReplies
  memeId: string
  onCommentAdded: () => void
}) => {
  const [showReplyForm, setShowReplyForm] = useState(false)

  const toggleReplyForm = () => {
    setShowReplyForm(!showReplyForm)
  }

  const handleReplyAdded = () => {
    setShowReplyForm(false)
    onCommentAdded()
  }

  return (
    <div className="mb-4">
      <div className="flex items-center space-x-2 mb-1">
        <Avatar className="w-6 h-6 border border-brand/20">
          <AvatarImage src={`https://api.dicebear.com/6.x/initials/svg?seed=${comment.author}`} />
          <AvatarFallback>{comment.author[0]}</AvatarFallback>
        </Avatar>
        <span className="font-semibold text-sm">{comment.author}</span>
        <span className="text-xs text-muted-foreground">
          {new Date(comment.created_at).toLocaleString(undefined, {
            dateStyle: "short",
            timeStyle: "short",
          })}
        </span>
      </div>
      <div className="ml-8">
        <p className="text-sm mb-2">{comment.content}</p>
        <Button
          variant="ghost"
          size="sm"
          onClick={toggleReplyForm}
          className="text-xs flex items-center h-6 px-2 py-1 comment-button"
        >
          <Reply className="h-3 w-3 mr-1" />
          Reply
        </Button>

        {showReplyForm && (
          <div className="mt-2 mb-3 pl-4 border-l-2 border-muted dark:border-muted">
            <CommentForm memeId={memeId} parentId={comment.id} onCommentAdded={handleReplyAdded} isReply={true} />
          </div>
        )}
      </div>

      {comment.replies && comment.replies.length > 0 && (
        <div className="ml-8 mt-3 pl-4 border-l-2 border-muted dark:border-muted">
          {comment.replies.map((reply) => (
            <CommentItem key={reply.id} comment={reply} memeId={memeId} onCommentAdded={onCommentAdded} />
          ))}
        </div>
      )}
    </div>
  )
}

export function CommentTree({ comments, memeId, onCommentAdded }: CommentTreeProps) {
  const [organizedComments, setOrganizedComments] = useState<CommentWithReplies[]>([])

  useEffect(() => {
    // Organize comments into a tree structure
    const commentMap = new Map<string, CommentWithReplies>()
    const rootComments: CommentWithReplies[] = []

    // First pass: create all comment objects
    comments.forEach((comment) => {
      commentMap.set(comment.id, { ...comment, replies: [] })
    })

    // Second pass: organize into tree
    comments.forEach((comment) => {
      const commentWithReplies = commentMap.get(comment.id)!

      if (comment.parent_id) {
        // This is a reply, add it to its parent
        const parent = commentMap.get(comment.parent_id)
        if (parent) {
          if (!parent.replies) {
            parent.replies = []
          }
          parent.replies.push(commentWithReplies)
        }
      } else {
        // This is a root comment
        rootComments.push(commentWithReplies)
      }
    })

    setOrganizedComments(rootComments)
  }, [comments])

  return (
    <div className="mt-4 bg-secondary/50 dark:bg-secondary/30 p-4 rounded-md">
      <h3 className="text-lg font-semibold mb-4">Comments</h3>

      {/* Comment form for new top-level comments */}
      <CommentForm memeId={memeId} onCommentAdded={onCommentAdded} />

      <div className="mt-6">
        {organizedComments.length > 0 ? (
          organizedComments.map((comment) => (
            <CommentItem key={comment.id} comment={comment} memeId={memeId} onCommentAdded={onCommentAdded} />
          ))
        ) : (
          <p className="text-center text-sm text-muted-foreground py-2">No comments yet. Be the first to comment!</p>
        )}
      </div>
    </div>
  )
}
