"use client"

import { useState, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { X, Filter } from "lucide-react"
import { supabase } from "@/lib/supabase"

interface TagFilterProps {
  onTagSelect: (tag: string | null) => void
  selectedTag: string | null
}

export function TagFilter({ onTagSelect, selectedTag }: TagFilterProps) {
  const [tags, setTags] = useState<string[]>([])
  const [isOpen, setIsOpen] = useState(false)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchTags()
  }, [])

  const fetchTags = async () => {
    try {
      setLoading(true)

      // Fetch all unique tags from the memes table
      const { data, error } = await supabase.from("memes").select("tag").not("tag", "is", null)

      if (error) {
        throw error
      }

      if (data) {
        // Extract unique tags
        const uniqueTags = Array.from(new Set(data.map((item) => item.tag)))
          .filter((tag) => tag) // Remove empty tags
          .sort() // Sort alphabetically

        setTags(uniqueTags)
      }
    } catch (error) {
      console.error("Error fetching tags:", error)
    } finally {
      setLoading(false)
    }
  }

  const toggleFilter = () => {
    setIsOpen(!isOpen)
  }

  const handleTagClick = (tag: string) => {
    onTagSelect(selectedTag === tag ? null : tag)
  }

  const clearFilter = () => {
    onTagSelect(null)
  }

  return (
    <div className="mb-6">
      <div className="flex items-center justify-between mb-2">
        <Button variant="outline" size="sm" onClick={toggleFilter} className="flex items-center nav-button">
          <Filter className="h-4 w-4 mr-2" />
          Filter by Tag
        </Button>

        {selectedTag && (
          <Badge className="flex items-center tag-badge-selected">
            {selectedTag}
            <Button
              variant="ghost"
              size="sm"
              onClick={clearFilter}
              className="h-5 w-5 p-0 ml-1 text-brand-foreground hover:bg-brand/80"
            >
              <X className="h-3 w-3" />
            </Button>
          </Badge>
        )}
      </div>

      {isOpen && (
        <div className="flex flex-wrap gap-2 mt-2 p-3 bg-card dark:bg-card rounded-md shadow-sm">
          {loading ? (
            <p className="text-sm text-muted-foreground">Loading tags...</p>
          ) : tags.length > 0 ? (
            tags.map((tag) => (
              <Badge
                key={tag}
                variant={selectedTag === tag ? "default" : "outline"}
                className={`cursor-pointer ${selectedTag === tag ? "tag-badge-selected" : "tag-badge"}`}
                onClick={() => handleTagClick(tag)}
              >
                {tag}
              </Badge>
            ))
          ) : (
            <p className="text-sm text-muted-foreground">No tags found</p>
          )}
        </div>
      )}
    </div>
  )
}
