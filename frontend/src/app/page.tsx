import Link from "next/link";

export default function Home() {
  return (
    <div className="relative min-h-screen overflow-hidden bg-background">
      {/* Background Decorative Elements */}
      <div className="absolute top-0 left-1/2 w-full -translate-x-1/2 overflow-hidden">
        <div className="absolute -top-[40rem] left-1/2 -z-10 h-[60rem] w-[90rem] -translate-x-1/2 bg-[radial-gradient(ellipse_at_top,rgba(16,185,129,0.15),transparent_50%)]" />
      </div>

      {/* Main Content */}
      <main className="relative z-10 flex min-h-screen flex-col items-center justify-center px-6 text-center">
        {/* Animated Badge */}
        <div className="mb-8 inline-flex animate-float items-center rounded-full border border-primary/30 bg-primary/10 px-4 py-2 text-sm font-medium text-primary backdrop-blur-sm">
          <span className="relative flex h-2 w-2 mr-2">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-primary opacity-75"></span>
            <span className="relative inline-flex rounded-full h-2 w-2 bg-primary"></span>
          </span>
          MealGenie v2.0 is Here
        </div>

        {/* Hero Headline */}
        <h1 className="max-w-4xl bg-gradient-to-br from-white to-slate-400 bg-clip-text text-5xl font-extrabold tracking-tight text-transparent sm:text-7xl">
          Your Personal <span className="text-primary">AI Kitchen</span> Swarm
        </h1>
        
        <p className="mx-auto mt-6 max-w-2xl text-lg text-slate-400 sm:text-xl">
          Snap a picture of your fridge. Let our dedicated team of AI Chefs, Nutritionists, and Sommeliers craft your perfect, sustainable meal in seconds.
        </p>

        {/* Action Buttons */}
        <div className="mt-10 flex flex-col sm:flex-row gap-4">
          <Link
            href="/dashboard"
            className="group relative inline-flex items-center justify-center overflow-hidden rounded-full bg-primary px-8 py-3.5 text-base font-semibold text-white transition-all hover:bg-primary-hover hover:scale-105 active:scale-95"
          >
            <div className="absolute inset-0 flex h-full w-full justify-center [transform:skew(-12deg)_translateX(-100%)] group-hover:duration-1000 group-hover:[transform:skew(-12deg)_translateX(100%)]">
              <div className="relative h-full w-8 bg-white/20" />
            </div>
            Get Started Free
            <svg className="ml-2 h-4 w-4 transition-transform group-hover:translate-x-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
            </svg>
          </Link>

          <Link
            href="#features"
            className="inline-flex items-center justify-center rounded-full border border-slate-700 bg-slate-800/50 px-8 py-3.5 text-base font-medium text-slate-300 backdrop-blur-md transition-all hover:bg-slate-800 hover:text-white"
          >
            View Features
          </Link>
        </div>

        {/* Features Glass Cards */}
        <div className="mt-24 grid w-full max-w-5xl grid-cols-1 gap-6 sm:grid-cols-3">
          <div className="glass-card p-6 text-left">
            <div className="mb-4 inline-flex rounded-lg bg-emerald-500/20 p-3 text-emerald-400">
              <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 9l9-7 9 7v11a2 2 0 01-2 2H5a2 2 0 01-2-2z" />
              </svg>
            </div>
            <h3 className="mb-2 text-xl font-semibold text-white">Pantry Vision</h3>
            <p className="text-sm text-slate-400">Upload an image of your ingredients and watch the magic happen automatically.</p>
          </div>

          <div className="glass-card p-6 text-left">
            <div className="mb-4 inline-flex rounded-lg bg-blue-500/20 p-3 text-blue-400">
              <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
              </svg>
            </div>
            <h3 className="mb-2 text-xl font-semibold text-white">Multi-Agent Swarm</h3>
            <p className="text-sm text-slate-400">A Head Chef, Nutritionist, and Sommelier collaborate to design your perfect plate.</p>
          </div>


        </div>
      </main>
    </div>
  );
}
