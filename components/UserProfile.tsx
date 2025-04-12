"use client"

import { useState } from "react"
import { UserButton } from "@clerk/nextjs"
import { UsernameDialog } from "./UsernameDialog"

export function UserProfile() {
    const [isUsernameDialogOpen, setIsUsernameDialogOpen] = useState(false)

    return (
        <>
            <UserButton
                afterSignOutUrl="/"
                appearance={{
                    elements: {
                        userButtonPopoverCard: "bg-card dark:bg-card text-card-foreground",
                        userButtonPopoverActionButton: "text-foreground hover:bg-accent",
                        userButtonPopoverActionButtonText: "text-foreground",
                        userButtonPopoverActionButtonIcon: "text-foreground",
                    },
                }}
                userProfileProps={{
                    appearance: {
                        elements: {
                            rootBox: "bg-card dark:bg-card text-card-foreground",
                            card: "bg-card dark:bg-card text-card-foreground",
                            navbar: "bg-card dark:bg-card text-card-foreground",
                            navbarButton: "text-foreground hover:bg-accent",
                            pageScrollBox: "bg-card dark:bg-card text-card-foreground",
                            headerTitle: "text-foreground",
                            headerSubtitle: "text-muted-foreground",
                            profileSectionTitleText: "text-foreground",
                            profileSectionTitleTextDanger: "text-destructive",
                            formButtonPrimary: "bg-primary hover:bg-primary/90",
                            formButtonReset: "text-foreground hover:bg-accent",
                            accordionTriggerButton: "text-foreground hover:bg-accent",
                            footerActionLink: "text-primary hover:text-primary/90",
                        },
                    },
                    additionalOAuthScopes: {
                        google: ["profile"],
                    },
                }}
            />
            <UsernameDialog open={isUsernameDialogOpen} onOpenChange={setIsUsernameDialogOpen} />
        </>
    )
} 
