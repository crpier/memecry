"use client"

import type React from "react"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Search, Shuffle, Sun, Moon, X } from "lucide-react"
import { CreateMemeForm } from "./CreateMemeForm"
import { useUser, SignInButton, SignUpButton } from "@clerk/nextjs"
import { UserProfile } from "@/components/UserProfile"

interface NavbarProps {
  darkMode: boolean
  toggleDarkMode: () => void
  onSearch: (query: string) => void
  onRandomMeme: () => void
  onMemeCreated: () => void
}

export function Navbar({ darkMode, toggleDarkMode, onSearch, onRandomMeme, onMemeCreated }: NavbarProps) {
  const [searchQuery, setSearchQuery] = useState("")
  const { isSignedIn } = useUser()

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault()
    onSearch(searchQuery)
  }

  const clearSearch = () => {
    setSearchQuery("")
    onSearch("")
  }

  return (
    <div className="sticky top-0 z-10 bg-secondary dark:bg-secondary shadow-md">
      <div className="container mx-auto px-4 max-w-6xl">
        <div className="flex items-center justify-between h-16">
          {/* Left section: Logo and Random button */}
          <div className="flex items-center space-x-2">
            <h1 className="text-xl font-bold text-brand">Memecry</h1>
            <Button
              variant="outline"
              size="sm"
              onClick={onRandomMeme}
              className="hidden sm:flex items-center nav-button"
            >
              <Shuffle className="h-4 w-4 mr-2" />
              Random
            </Button>
          </div>

          {/* Center: Search Bar - Hide on mobile */}
          <div className="hidden md:block flex-1 max-w-md mx-4">
            <form onSubmit={handleSearch} className="relative">
              <Input
                type="text"
                placeholder="Search..."
                className="w-full pl-10 pr-10 bg-background dark:bg-background"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
              />
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
              {searchQuery && (
                <Button
                  type="button"
                  variant="ghost"
                  size="sm"
                  onClick={clearSearch}
                  className="absolute right-1 top-1/2 transform -translate-y-1/2 h-7 w-7 p-0"
                >
                  <X className="h-4 w-4" />
                </Button>
              )}
            </form>
          </div>

          {/* Right: Auth Buttons and Create Meme */}
          <div className="flex items-center space-x-2">
            {isSignedIn ? (
              <>
                <CreateMemeForm onMemeCreated={onMemeCreated} />
                <UserProfile />
              </>
            ) : (
              <>
                <SignUpButton mode="modal">
                  <Button variant="outline" size="sm" className="hidden sm:inline-flex nav-button">
                    Sign Up
                  </Button>
                </SignUpButton>
                <SignInButton mode="modal">
                  <Button size="sm" className="primary-button">
                    Log In
                  </Button>
                </SignInButton>
              </>
            )}
            <Button variant="ghost" size="icon" onClick={toggleDarkMode}>
              {darkMode ? <Sun className="h-5 w-5 text-brand" /> : <Moon className="h-5 w-5" />}
            </Button>
          </div>
        </div>

        {/* Mobile Search Bar */}
        <div className="md:hidden pb-3">
          <form onSubmit={handleSearch} className="relative">
            <Input
              type="text"
              placeholder="Search..."
              className="w-full pl-10 pr-10 bg-background dark:bg-background"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
            {searchQuery && (
              <Button
                type="button"
                variant="ghost"
                size="sm"
                onClick={clearSearch}
                className="absolute right-1 top-1/2 transform -translate-y-1/2 h-7 w-7 p-0"
              >
                <X className="h-4 w-4" />
              </Button>
            )}
          </form>
        </div>
      </div>
    </div>
  )
}
