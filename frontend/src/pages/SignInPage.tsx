import { SignIn } from "@clerk/clerk-react";

export default function SignInPage() {
  return (
    <div className="flex justify-center items-center h-screen">
      <SignIn afterSignInUrl="/dashboard" redirectUrl="/dashboard" />
    </div>
  );
}
