"use client"

import { useState } from "react"
import { useUser } from "@clerk/nextjs"
import {
    Dialog,
    DialogContent,
    DialogDescription,
    DialogHeader,
    DialogTitle,
} from "@/components/ui/dialog"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { toast } from "sonner"

interface UsernameDialogProps {
    open: boolean
    onOpenChange: (open: boolean) => void
    onUsernameSet?: () => void
}

export function UsernameDialog({ open, onOpenChange, onUsernameSet }: UsernameDialogProps) {
    const { user } = useUser()
    const [username, setUsername] = useState("")
    const [isLoading, setIsLoading] = useState(false)

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault()
        if (!user) return

        setIsLoading(true)
        try {
            await user.update({ username })
            toast.success("Username updated successfully")
            onUsernameSet?.()
            onOpenChange(false)
        } catch (err) {
            toast.error("Failed to update username")
            console.error(err)
        } finally {
            setIsLoading(false)
        }
    }

    return (
        <Dialog open={open} onOpenChange={onOpenChange}>
            <DialogContent>
                <DialogHeader>
                    <DialogTitle>Set Your Username</DialogTitle>
                    <DialogDescription>
                        Choose a unique username for your account.
                    </DialogDescription>
                </DialogHeader>
                <form onSubmit={handleSubmit} className="space-y-4">
                    <Input
                        placeholder="Enter username"
                        value={username}
                        onChange={(e) => setUsername(e.target.value)}
                        required
                    />
                    <Button type="submit" disabled={isLoading}>
                        {isLoading ? "Saving..." : "Save Username"}
                    </Button>
                </form>
            </DialogContent>
        </Dialog>
    )
} 