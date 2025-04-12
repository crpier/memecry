"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from "@/components/ui/dialog"
import { PlusCircle, Loader2 } from "lucide-react"
import { useUser } from "@clerk/nextjs"

interface CreateMemeFormProps {
  onMemeCreatedAction: () => void
}

export function CreateMemeForm({ onMemeCreatedAction }: CreateMemeFormProps) {
  const [open, setOpen] = useState(false)
  const [title, setTitle] = useState("")
  const [imageUrl, setImageUrl] = useState("")
  const [tag, setTag] = useState("")
  const [error, setError] = useState("")
  const [isSubmitting, setIsSubmitting] = useState(false)
  const { user } = useUser()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsSubmitting(true)
    setError("")

    try {
      const response = await fetch("/api/memes", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          title,
          image_url: imageUrl,
          author: user?.username || user?.firstName || "Anonymous",
          tag,
        }),
      })

      if (!response.ok) {
        throw new Error("Failed to create meme")
      }

      setOpen(false)
      onMemeCreatedAction()
    } catch {
      setError("Failed to create meme. Please try again.")
    } finally {
      setIsSubmitting(false)
    }
  }

  if (!user) return null

  return (
    <>
      <Button onClick={() => setOpen(true)} className="flex items-center space-x-1 primary-button" size="sm">
        <PlusCircle className="h-4 w-4 mr-1" />
        Create Meme
      </Button>

      <Dialog open={open} onOpenChange={setOpen}>
        <DialogContent className="sm:max-w-[425px] bg-card dark:bg-card text-card-foreground">
          <DialogHeader>
            <DialogTitle>Create New Meme</DialogTitle>
            <DialogDescription className="text-muted-foreground">
              Fill out the form below to create a new meme. Click save when you are done.
            </DialogDescription>
          </DialogHeader>

          <form onSubmit={handleSubmit} className="space-y-4 py-4">
            <div className="space-y-2">
              <Label htmlFor="title">Title</Label>
              <Input
                id="title"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                placeholder="Enter a catchy title"
                className="bg-background dark:bg-background"
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="imageUrl">Image URL</Label>
              <Input
                id="imageUrl"
                value={imageUrl}
                onChange={(e) => setImageUrl(e.target.value)}
                placeholder="https://example.com/your-meme.jpg"
                className="bg-background dark:bg-background"
              />
              <p className="text-xs text-muted-foreground">Paste a direct link to your meme image</p>
            </div>

            <div className="space-y-2">
              <Label htmlFor="tag">Tag (optional)</Label>
              <Input
                id="tag"
                value={tag}
                onChange={(e) => setTag(e.target.value)}
                placeholder="Funny, Tech, Relatable, etc."
                className="bg-background dark:bg-background"
              />
            </div>

            {error && <p className="text-sm text-destructive">{error}</p>}

            <DialogFooter>
              <Button type="button" variant="outline" onClick={() => setOpen(false)} className="nav-button">
                Cancel
              </Button>
              <Button type="submit" disabled={isSubmitting} className="primary-button">
                {isSubmitting ? (
                  <>
                    <Loader2 className="h-4 w-4 animate-spin mr-2" />
                    Creating...
                  </>
                ) : (
                  "Create Meme"
                )}
              </Button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>
    </>
  )
}
