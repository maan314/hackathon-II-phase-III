'use client';

import Link from 'next/link';
import { useEffect } from 'react';
import { useRouter } from 'next/navigation';

export default function HomePage() {
  const router = useRouter();

  useEffect(() => {
    const token = typeof window !== 'undefined' ? localStorage.getItem('token') : null;
    if (token) {
      router.replace('/dashboard');
    }
  }, [router]);

  return (
    <div className="relative min-h-screen overflow-hidden bg-black">
      {/* Animated Background Gradient */}
      <div className="absolute inset-0 bg-gradient-to-br from-purple-900/20 via-black to-cyan-900/20" />

      {/* Animated Glow Orbs */}
      <div className="absolute top-20 left-20 w-96 h-96 bg-purple-500/30 rounded-full blur-3xl animate-pulse" />
      <div className="absolute bottom-20 right-20 w-96 h-96 bg-cyan-500/30 rounded-full blur-3xl animate-pulse" />

      {/* Grid Pattern Overlay */}
      <div className="absolute inset-0 bg-[linear-gradient(rgba(139,92,246,0.03)_1px,transparent_1px),linear-gradient(90deg,rgba(139,92,246,0.03)_1px,transparent_1px)] bg-[size:50px_50px]" />

      {/* Main Content */}
      <div className="relative z-10 container mx-auto px-6 py-20 flex flex-col items-center justify-center min-h-screen">

        {/* Hero Section */}
        <div className="text-center space-y-8">

          {/* App Name with Neon Glow */}
          <div className="space-y-4">
            <h1 className="text-6xl md:text-7xl font-bold tracking-tight">
              <span className="bg-gradient-to-r from-cyan-400 via-purple-400 to-pink-400 bg-clip-text text-transparent animate-gradient-x drop-shadow-[0_0_30px_rgba(139,92,246,0.5)]">
                Todo Management App
              </span>
            </h1>
            <div className="h-1 w-64 mx-auto bg-gradient-to-r from-transparent via-purple-500 to-transparent animate-pulse" />
          </div>

          {/* Tagline */}
          <p className="text-2xl md:text-3xl text-gray-300 font-light">
            Intelligent Task Management
            <span className="text-cyan-400"> Powered by AI</span>
          </p>

          {/* Description */}
          <p className="text-lg text-gray-400 max-w-2xl mx-auto leading-relaxed">
            Experience the future of productivity with our AI-powered task management system.
            Create, organize, and complete tasks using natural language commands with our intelligent assistant.
          </p>

          {/* Feature Cards */}
          <div className="grid md:grid-cols-3 gap-6 mt-16">

            {/* Feature 1 */}
            <div className="group relative p-6 rounded-2xl bg-gradient-to-br from-purple-900/20 to-transparent border border-purple-500/20 hover:border-purple-500/50 transition-all duration-300 hover:scale-105">
              <div className="absolute inset-0 bg-gradient-to-br from-purple-500/10 to-transparent rounded-2xl opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
              <div className="relative">
                <div className="w-12 h-12 mb-4 rounded-lg bg-purple-500/20 flex items-center justify-center text-purple-400 text-2xl">
                  🤖
                </div>
                <h3 className="text-xl font-semibold text-white mb-2">AI Assistant</h3>
                <p className="text-gray-400 text-sm">
                  Chat with our intelligent AI to manage tasks using natural language commands
                </p>
              </div>
            </div>

            {/* Feature 2 */}
            <div className="group relative p-6 rounded-2xl bg-gradient-to-br from-cyan-900/20 to-transparent border border-cyan-500/20 hover:border-cyan-500/50 transition-all duration-300 hover:scale-105">
              <div className="absolute inset-0 bg-gradient-to-br from-cyan-500/10 to-transparent rounded-2xl opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
              <div className="relative">
                <div className="w-12 h-12 mb-4 rounded-lg bg-cyan-500/20 flex items-center justify-center text-cyan-400 text-2xl">
                  ⚡
                </div>
                <h3 className="text-xl font-semibold text-white mb-2">Real-time Sync</h3>
                <p className="text-gray-400 text-sm">
                  Your tasks sync instantly across all devices with cloud-powered storage
                </p>
              </div>
            </div>

            {/* Feature 3 */}
            <div className="group relative p-6 rounded-2xl bg-gradient-to-br from-pink-900/20 to-transparent border border-pink-500/20 hover:border-pink-500/50 transition-all duration-300 hover:scale-105">
              <div className="absolute inset-0 bg-gradient-to-br from-pink-500/10 to-transparent rounded-2xl opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
              <div className="relative">
                <div className="w-12 h-12 mb-4 rounded-lg bg-pink-500/20 flex items-center justify-center text-pink-400 text-2xl">
                  🎯
                </div>
                <h3 className="text-xl font-semibold text-white mb-2">Smart Organization</h3>
                <p className="text-gray-400 text-sm">
                  Automatically organize and prioritize tasks with intelligent categorization
                </p>
              </div>
            </div>
          </div>

          {/* CTA Buttons */}
          <div className="flex flex-col sm:flex-row gap-6 justify-center items-center mt-16">

            {/* Sign Up Button */}
            <Link href="/signup">
              <button className="group relative px-8 py-4 rounded-xl font-semibold text-lg overflow-hidden transition-all duration-300 hover:scale-105">
                <div className="absolute inset-0 bg-gradient-to-r from-purple-600 to-pink-600 transition-all duration-300 group-hover:from-purple-500 group-hover:to-pink-500" />
                <div className="absolute inset-0 bg-gradient-to-r from-purple-600 to-pink-600 blur-xl opacity-50 group-hover:opacity-75 transition-opacity duration-300" />
                <span className="relative text-white flex items-center gap-2">
                  Get Started Free
                  <span className="group-hover:translate-x-1 transition-transform duration-300">→</span>
                </span>
              </button>
            </Link>

            {/* Sign In Button */}
            <Link href="/signin">
              <button className="group relative px-8 py-4 rounded-xl font-semibold text-lg border-2 border-cyan-500/50 text-cyan-400 hover:border-cyan-400 hover:text-cyan-300 transition-all duration-300 hover:scale-105 hover:shadow-[0_0_30px_rgba(34,211,238,0.3)]">
                Sign In
              </button>
            </Link>
          </div>

          {/* Stats Section */}
          <div className="grid grid-cols-3 gap-8 mt-20 pt-12 border-t border-purple-500/20">
            <div className="text-center">
              <div className="text-4xl font-bold bg-gradient-to-r from-purple-400 to-pink-400 bg-clip-text text-transparent">
                10K+
              </div>
              <div className="text-gray-500 text-sm mt-2">Active Users</div>
            </div>
            <div className="text-center">
              <div className="text-4xl font-bold bg-gradient-to-r from-cyan-400 to-purple-400 bg-clip-text text-transparent">
                50K+
              </div>
              <div className="text-gray-500 text-sm mt-2">Tasks Completed</div>
            </div>
            <div className="text-center">
              <div className="text-4xl font-bold bg-gradient-to-r from-pink-400 to-cyan-400 bg-clip-text text-transparent">
                99.9%
              </div>
              <div className="text-gray-500 text-sm mt-2">Uptime</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
