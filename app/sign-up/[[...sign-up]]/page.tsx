import { SignUp } from "@clerk/nextjs";

export default function Page() {
    return (
        <div className="min-h-screen flex items-center justify-center bg-background">
            <SignUp
                appearance={{
                    elements: {
                        formButtonPrimary: "bg-primary hover:bg-primary/90",
                        footerActionLink: "text-primary hover:text-primary/90"
                    }
                }}
            />
        </div>
    );
} 