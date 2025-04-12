"use client"

import { useState, useEffect, useRef, useCallback } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader } from "@/components/ui/card"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { Separator } from "@/components/ui/separator"
import { ArrowUpFromLine, ArrowDownToLine, MessageSquare, Loader2 } from "lucide-react"
import { motion, AnimatePresence } from "framer-motion"
import { CommentTree } from "@/components/CommentTree"
import { TagFilter } from "@/components/TagFilter"
import { supabase, type DbMeme, type DbComment } from "@/lib/supabase"
import { formatDistanceToNow } from "date-fns"

// Number of memes to load per page
const PAGE_SIZE = 5

export default function MemeViewer() {
  const [memes, setMemes] = useState<DbMeme[]>([])
  const [filteredMemes, setFilteredMemes] = useState<DbMeme[]>([])
  const [comments, setComments] = useState<Record<string, DbComment[]>>({})
  const [expandedComments, setExpandedComments] = useState<string[]>([])
  const [loading, setLoading] = useState(true)
  const [loadingMore, setLoadingMore] = useState(false)
  const [hasMore, setHasMore] = useState(true)
  const [searchQuery, setSearchQuery] = useState("")
  const [selectedTag, setSelectedTag] = useState<string | null>(null)
  const [page, setPage] = useState(0)
  const [votedMemes, setVotedMemes] = useState<Record<string, "like" | "dislike" | null>>({})

  // Reference to the sentinel element for infinite scrolling
  const observerRef = useRef<IntersectionObserver | null>(null)
  const sentinelRef = useRef<HTMLDivElement | null>(null)

  useEffect(() => {
    // Initial load
    fetchMemes(0, true)
  }, [])

  const applyFilters = () => {
    let filtered = [...memes]

    // Apply tag filter
    if (selectedTag) {
      filtered = filtered.filter((meme) => meme.tag === selectedTag)
    }

    // Apply search filter
    if (searchQuery) {
      filtered = filtered.filter(
        (meme) =>
          meme.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
          meme.author.toLowerCase().includes(searchQuery.toLowerCase()) ||
          (meme.tag && meme.tag.toLowerCase().includes(searchQuery.toLowerCase())),
      )
    }

    setFilteredMemes(filtered)

    // Disable infinite scrolling when filtering
    setHasMore(!searchQuery && !selectedTag && memes.length % PAGE_SIZE === 0 && memes.length > 0)
  }
  useEffect(() => {
    // Apply filters when search query or selected tag changes
    applyFilters()
  }, [searchQuery, selectedTag, memes])


  // Setup intersection observer for infinite scrolling
  const lastMemeElementRef = useCallback(
    (node: HTMLDivElement | null) => {
      if (sentinelRef.current) {
        sentinelRef.current = node
      }

      if (observerRef.current) {
        observerRef.current.disconnect()
      }

      observerRef.current = new IntersectionObserver(
        (entries) => {
          if (entries[0].isIntersecting && hasMore && !loadingMore && !searchQuery && !selectedTag) {
            loadMoreMemes()
          }
        },
        { threshold: 0.5 },
      )

      if (node) {
        observerRef.current.observe(node)
        sentinelRef.current = node
      }
    },
    [hasMore, loadingMore, searchQuery, selectedTag],
  )

  const fetchMemes = async (pageNum: number, reset = false) => {
    try {
      if (reset) {
        setLoading(true)
      } else {
        setLoadingMore(true)
      }

      const from = pageNum * PAGE_SIZE
      const to = from + PAGE_SIZE - 1

      const { data, error } = await supabase
        .from("memes")
        .select("*")
        .order("created_at", { ascending: false })
        .range(from, to)

      if (error) {
        throw error
      }

      if (data) {
        if (reset) {
          setMemes(data)
        } else {
          setMemes((prev) => [...prev, ...data])
        }

        // Check if we have more memes to load
        setHasMore(data.length === PAGE_SIZE)
      }
    } catch (error) {
      console.error("Error fetching memes:", error)
    } finally {
      setLoading(false)
      setLoadingMore(false)
    }
  }

  const loadMoreMemes = () => {
    const nextPage = page + 1
    setPage(nextPage)
    fetchMemes(nextPage)
  }

  const fetchComments = async (memeId: string) => {
    try {
      const { data, error } = await supabase
        .from("comments")
        .select("*")
        .eq("meme_id", memeId)
        .order("created_at", { ascending: true })

      if (error) {
        throw error
      }

      if (data) {
        setComments((prev) => ({
          ...prev,
          [memeId]: data,
        }))
      }
    } catch (error) {
      console.error("Error fetching comments:", error)
    }
  }

  const handleCommentAdded = async (memeId: string) => {
    // Refresh comments for this meme
    await fetchComments(memeId)
  }

  const handleVote = async (id: string, type: "like" | "dislike") => {
    try {
      // Check if user already voted on this meme
      const currentVote = votedMemes[id] || null

      // If user is clicking the same vote type again, remove their vote
      if (currentVote === type) {
        // Remove vote
        setVotedMemes((prev) => ({
          ...prev,
          [id]: null,
        }))

        // Optimistic update to remove vote
        setMemes((prev) =>
          prev.map((meme) => {
            if (meme.id === id) {
              if (type === "like") {
                return { ...meme, likes: meme.likes - 1 }
              } else {
                return { ...meme, dislikes: meme.dislikes - 1 }
              }
            }
            return meme
          }),
        )

        // Update filtered memes
        setFilteredMemes((prev) =>
          prev.map((meme) => {
            if (meme.id === id) {
              if (type === "like") {
                return { ...meme, likes: meme.likes - 1 }
              } else {
                return { ...meme, dislikes: meme.dislikes - 1 }
              }
            }
            return meme
          }),
        )

        // Update in database
        const { error } = await supabase
          .from("memes")
          .update({
            [type === "like" ? "likes" : "dislikes"]:
              type === "like"
                ? Math.max(0, memes.find((m) => m.id === id)!.likes - 1)
                : Math.max(0, memes.find((m) => m.id === id)!.dislikes - 1),
          })
          .eq("id", id)

        if (error) throw error
      } else {
        // Set new vote
        setVotedMemes((prev) => ({
          ...prev,
          [id]: type,
        }))

        // If user is changing their vote, we need to decrement the previous vote type
        if (currentVote) {
          // Optimistic update to change vote
          setMemes((prev) =>
            prev.map((meme) => {
              if (meme.id === id) {
                if (type === "like") {
                  return {
                    ...meme,
                    likes: meme.likes + 1,
                    dislikes: meme.dislikes - 1,
                  }
                } else {
                  return {
                    ...meme,
                    likes: meme.likes - 1,
                    dislikes: meme.dislikes + 1,
                  }
                }
              }
              return meme
            }),
          )

          // Update filtered memes
          setFilteredMemes((prev) =>
            prev.map((meme) => {
              if (meme.id === id) {
                if (type === "like") {
                  return {
                    ...meme,
                    likes: meme.likes + 1,
                    dislikes: meme.dislikes - 1,
                  }
                } else {
                  return {
                    ...meme,
                    likes: meme.likes - 1,
                    dislikes: meme.dislikes + 1,
                  }
                }
              }
              return meme
            }),
          )

          // Update in database
          const { error } = await supabase
            .from("memes")
            .update({
              likes:
                type === "like"
                  ? memes.find((m) => m.id === id)!.likes + 1
                  : Math.max(0, memes.find((m) => m.id === id)!.likes - 1),
              dislikes:
                type === "dislike"
                  ? memes.find((m) => m.id === id)!.dislikes + 1
                  : Math.max(0, memes.find((m) => m.id === id)!.dislikes - 1),
            })
            .eq("id", id)

          if (error) throw error
        } else {
          // Simple vote (no previous vote)
          // Optimistic update
          setMemes((prev) =>
            prev.map((meme) => {
              if (meme.id === id) {
                if (type === "like") {
                  return { ...meme, likes: meme.likes + 1 }
                } else {
                  return { ...meme, dislikes: meme.dislikes + 1 }
                }
              }
              return meme
            }),
          )

          // Also update filtered memes
          setFilteredMemes((prev) =>
            prev.map((meme) => {
              if (meme.id === id) {
                if (type === "like") {
                  return { ...meme, likes: meme.likes + 1 }
                } else {
                  return { ...meme, dislikes: meme.dislikes + 1 }
                }
              }
              return meme
            }),
          )

          // Update in database
          const { error } = await supabase
            .from("memes")
            .update({
              [type === "like" ? "likes" : "dislikes"]:
                type === "like"
                  ? memes.find((m) => m.id === id)!.likes + 1
                  : memes.find((m) => m.id === id)!.dislikes + 1,
            })
            .eq("id", id)

          if (error) throw error
        }
      }
    } catch (error) {
      console.error("Error updating vote:", error)
      // Revert optimistic update on error
      fetchMemes(0, true)
    }
  }

  const toggleComments = async (id: string) => {
    if (!expandedComments.includes(id)) {
      // If we're expanding comments and haven't loaded them yet
      if (!comments[id]) {
        await fetchComments(id)
      }
    }

    setExpandedComments((prev) => (prev.includes(id) ? prev.filter((memeId) => memeId !== id) : [...prev, id]))
  }

  const handleTagSelect = (tag: string | null) => {
    setSelectedTag(tag)
    // Reset to first page when changing tag filter
    setPage(0)
  }

  const formatTimeAgo = (dateString: string) => {
    try {
      return formatDistanceToNow(new Date(dateString), { addSuffix: true })
    } catch {
      return dateString
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-background text-foreground flex items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin mr-2 text-brand" />
        <span>Loading memes...</span>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-background text-foreground">
      <main className="container mx-auto py-8 px-4 max-w-lg">
        {/* Tag filter component */}
        <TagFilter onTagSelect={handleTagSelect} selectedTag={selectedTag} />

        {filteredMemes.length === 0 ? (
          <div className="text-center py-10">
            <p>No memes found matching your criteria.</p>
            {(searchQuery || selectedTag) && (
              <Button
                variant="outline"
                className="mt-4 nav-button"
                onClick={() => {
                  setSearchQuery("")
                  setSelectedTag(null)
                }}
              >
                Clear Filters
              </Button>
            )}
          </div>
        ) : (
          <div className="space-y-6">
            {filteredMemes.map((meme, index) => (
              <motion.div
                key={meme.id}
                id={`meme-${meme.id}`}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.3 }}
                className="transition-all duration-500"
                ref={index === filteredMemes.length - 1 ? lastMemeElementRef : null}
              >
                <Card className="bg-card text-card-foreground overflow-hidden shadow-sm card-hover">
                  <CardHeader className="p-3 pb-0">
                    <h2 className="text-lg font-semibold">{meme.title}</h2>
                  </CardHeader>
                  <CardContent className="p-3 space-y-3">
                    <img
                      src={meme.image_url || "/placeholder.svg"}
                      alt={meme.title}
                      className="w-full h-auto rounded-md"
                    />
                    <div className="flex items-center justify-between text-sm">
                      <Button
                        variant="outline"
                        size="sm"
                        className={`rounded-full text-xs ${selectedTag === meme.tag ? "tag-badge-selected" : "tag-badge"
                          }`}
                        onClick={() => handleTagSelect(meme.tag)}
                      >
                        {meme.tag}
                      </Button>
                      <div className="flex items-center space-x-2">
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => handleVote(meme.id, "like")}
                          className={`p-0 h-auto ${votedMemes[meme.id] === "like" ? "vote-button-active" : "vote-button"
                            }`}
                        >
                          <ArrowUpFromLine className="h-4 w-4" />
                        </Button>
                        <span className="text-sm font-semibold">{meme.likes - meme.dislikes}</span>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => handleVote(meme.id, "dislike")}
                          className={`p-0 h-auto ${votedMemes[meme.id] === "dislike" ? "vote-button-active" : "vote-button"
                            }`}
                        >
                          <ArrowDownToLine className="h-4 w-4" />
                        </Button>
                      </div>
                    </div>
                    <Separator className="my-2" />
                    <div className="flex items-center justify-between text-xs">
                      <div className="flex items-center space-x-2">
                        <Avatar className="w-5 h-5 border border-brand/20">
                          <AvatarImage src={`https://api.dicebear.com/6.x/initials/svg?seed=${meme.author}`} />
                          <AvatarFallback>{meme.author[0]}</AvatarFallback>
                        </Avatar>
                        <span>{meme.author}</span>
                        <span className="text-muted-foreground">• {formatTimeAgo(meme.created_at)}</span>
                      </div>
                      <Button
                        variant="ghost"
                        size="sm"
                        className="flex items-center space-x-1 p-0 h-auto comment-button"
                        onClick={() => toggleComments(meme.id)}
                      >
                        <MessageSquare className="h-3 w-3" />
                        <span>{comments[meme.id]?.length || 0}</span>
                      </Button>
                    </div>
                    <AnimatePresence>
                      {expandedComments.includes(meme.id) && (
                        <motion.div
                          initial={{ opacity: 0, height: 0 }}
                          animate={{ opacity: 1, height: "auto" }}
                          exit={{ opacity: 0, height: 0 }}
                          transition={{ duration: 0.3 }}
                        >
                          <CommentTree
                            comments={comments[meme.id] || []}
                            memeId={meme.id}
                            onCommentAdded={() => handleCommentAdded(meme.id)}
                          />
                        </motion.div>
                      )}
                    </AnimatePresence>
                  </CardContent>
                </Card>
              </motion.div>
            ))}

            {/* Loading indicator for infinite scrolling */}
            {loadingMore && (
              <div className="flex justify-center items-center py-4">
                <Loader2 className="h-6 w-6 animate-spin mr-2 text-brand" />
                <span>Loading more memes...</span>
              </div>
            )}

            {/* Sentinel element for intersection observer */}
            {hasMore && !loadingMore && !searchQuery && !selectedTag && (
              <div ref={lastMemeElementRef} className="h-10" />
            )}

            {/* End of content message */}
            {!hasMore && !loadingMore && filteredMemes.length > 0 && !searchQuery && !selectedTag && (
              <div className="text-center py-4 text-muted-foreground">You have reached the end of the memes!</div>
            )}
          </div>
        )}
      </main>
    </div>
  )
}
