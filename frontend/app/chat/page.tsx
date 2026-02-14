'use client';

import { useState, useRef, useEffect } from 'react';
import { useAuth } from '@/lib/auth-context';
import { useActivity } from '@/lib/activity-context';
import { useRouter } from 'next/navigation';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { ChatMessage } from '@/components/ui/chat-message';
import Link from 'next/link';

// Force dynamic rendering to prevent static generation issues with context
export const dynamic = 'force-dynamic';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
  toolCalls?: Array<{
    tool_name: string;
    status: string;
  }>;
}

export default function ChatPage() {
  const { user, isLoading } = useAuth();
  const { logActivity } = useActivity();
  const router = useRouter();
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isSending, setIsSending] = useState(false);
  const [conversationId, setConversationId] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  // Auto-focus input on mount and after sending completes
  useEffect(() => {
    if (!isSending) {
      inputRef.current?.focus();
    }
  }, [isSending]);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  if (isLoading) {
    return (
      <div className="container mx-auto flex min-h-[calc(100vh-4rem)] items-center justify-center py-10">
        <p className="text-white">Loading chat...</p>
      </div>
    );
  }

  if (!user) {
    router.push('/signin');
    return null;
  }

  const sendMessage = async () => {
    if (!input.trim() || isSending) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: input,
      timestamp: new Date().toISOString(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setIsSending(true);

    try {
      const chatApiUrl = process.env.NEXT_PUBLIC_CHAT_API_URL || process.env.NEXT_PUBLIC_API_URL || 'https://maan143-hackathon-ii-phase-ii-backend.hf.space';
      const response = await fetch(`${chatApiUrl}/api/${user.id}/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
        },
        body: JSON.stringify({
          message: input,
          conversation_id: conversationId,
        }),
      });

      if (!response.ok) {
        if (response.status === 401) {
          // Token expired - redirect to sign in
          localStorage.removeItem('token');
          router.push('/signin?expired=true');
          return;
        }
        throw new Error('Failed to send message');
      }

      const data = await response.json();

      if (!conversationId && data.conversation_id) {
        setConversationId(data.conversation_id);
      }

      const assistantMessage: Message = {
        id: data.message_id || Date.now().toString(),
        role: 'assistant',
        content: data.response,
        timestamp: data.timestamp,
        toolCalls: data.tool_calls,
      };

      setMessages((prev) => [...prev, assistantMessage]);

      // Log activities for successful tool calls with task details from response
      if (data.tool_calls && Array.isArray(data.tool_calls)) {
        const responseText = data.response.toLowerCase();

        data.tool_calls.forEach((toolCall: { tool_name: string; status: string }) => {
          if (toolCall.status === 'success') {
            // Try to extract task information from the AI's response
            let taskInfo = '';

            // Extract task name/ID from response text
            // Look for patterns like "task 'Name'" or "task ID X"
            const taskNameMatch = data.response.match(/['"]([^'"]+)['"]/);
            const taskIdMatch = data.response.match(/task (\d+)/i);

            if (taskNameMatch) {
              taskInfo = taskNameMatch[1];
            } else if (taskIdMatch) {
              taskInfo = `task ${taskIdMatch[1]}`;
            }

            // Map tool names to activity types and descriptions
            switch (toolCall.tool_name) {
              case 'add_task':
                logActivity({
                  action: taskInfo ? `Created "${taskInfo}"` : 'Created a task',
                  type: 'task-created'
                });
                break;
              case 'complete_task':
                logActivity({
                  action: taskInfo ? `Completed "${taskInfo}"` : 'Completed a task',
                  type: 'task-completed'
                });
                break;
              case 'reopen_task':
                logActivity({
                  action: taskInfo ? `Reopened "${taskInfo}"` : 'Reopened a task',
                  type: 'task-edited'
                });
                break;
              case 'update_task':
                logActivity({
                  action: taskInfo ? `Updated "${taskInfo}"` : 'Updated a task',
                  type: 'task-edited'
                });
                break;
              case 'delete_task':
                logActivity({
                  action: taskInfo ? `Deleted "${taskInfo}"` : 'Deleted a task',
                  type: 'task-deleted'
                });
                break;
              // list_tasks and get_task don't need activity logging (read-only)
            }
          }
        });
      }
    } catch (error) {
      console.error('Error sending message:', error);
      const errorMessage: Message = {
        id: Date.now().toString(),
        role: 'assistant',
        content: 'Sorry, I encountered an error. Please try again or check your connection.',
        timestamp: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsSending(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const startNewConversation = () => {
    setMessages([]);
    setConversationId(null);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-black text-white">
      <div className="flex flex-col h-screen">
        {/* ===== CHAT NAVBAR ===== */}
        <nav className="flex-shrink-0 h-14 md:h-16 border-b border-gray-700/50 bg-gray-900/80 backdrop-blur-md flex items-center justify-between px-3 md:px-6 sticky top-0 z-50">
          {/* Left: Back + Title */}
          <div className="flex items-center gap-2 md:gap-3 min-w-0">
            <Link
              href="/dashboard"
              className="flex-shrink-0 p-2 rounded-lg hover:bg-gray-800 transition-colors text-gray-400 hover:text-cyan-400"
              title="Back to Dashboard"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
              </svg>
            </Link>
            <div className="min-w-0">
              <h1 className="text-lg md:text-xl font-bold bg-gradient-to-r from-cyan-400 via-purple-500 to-pink-500 bg-clip-text text-transparent truncate">
                AI Assistant
              </h1>
              <p className="text-gray-500 text-xs hidden sm:block">Chat with your AI-powered task assistant</p>
            </div>
          </div>

          {/* Right: New Chat + Dashboard */}
          <div className="flex items-center gap-2 flex-shrink-0">
            <Button
              onClick={startNewConversation}
              variant="outline"
              size="sm"
              className="border-purple-500/40 text-purple-400 hover:bg-purple-500/10 hover:border-purple-500/60 text-xs md:text-sm"
            >
              <svg className="w-4 h-4 md:mr-1.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
              </svg>
              <span className="hidden sm:inline">New Chat</span>
            </Button>
            <Link href="/dashboard">
              <Button
                variant="outline"
                size="sm"
                className="border-cyan-500/40 text-cyan-400 hover:bg-cyan-500/10 hover:border-cyan-500/60 text-xs md:text-sm"
              >
                <svg className="w-4 h-4 md:mr-1.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2V6zM14 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V6zM4 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2v-2zM14 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z" />
                </svg>
                <span className="hidden sm:inline">Dashboard</span>
              </Button>
            </Link>
          </div>
        </nav>

        {/* ===== CHAT MESSAGES ===== */}
        <div className="flex-1 overflow-y-auto px-3 md:px-6 py-4">
          {messages.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-full text-center px-4">
              <div className="w-16 h-16 md:w-20 md:h-20 rounded-full bg-gradient-to-r from-cyan-500 to-purple-600 flex items-center justify-center mb-4 md:mb-6">
                <svg className="w-8 h-8 md:w-10 md:h-10" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
                </svg>
              </div>
              <h2 className="text-xl md:text-2xl font-bold mb-3 md:mb-4 bg-gradient-to-r from-cyan-400 to-purple-500 bg-clip-text text-transparent">
                Start a Conversation
              </h2>
              <p className="text-gray-400 mb-5 md:mb-6 max-w-md text-sm md:text-base">
                Ask me to help you manage your tasks, create new todos, mark tasks as complete, or get information about your task list.
              </p>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 md:gap-3 max-w-2xl w-full">
                <button
                  onClick={() => setInput("Create a task to review the proposal")}
                  className="px-3 md:px-4 py-2.5 md:py-3 rounded-lg border border-cyan-500/30 bg-cyan-500/5 hover:bg-cyan-500/10 transition-all duration-300 text-left text-xs md:text-sm"
                >
                  <span className="text-cyan-400">💡</span> Create a task to review the proposal
                </button>
                <button
                  onClick={() => setInput("Show me my pending tasks")}
                  className="px-3 md:px-4 py-2.5 md:py-3 rounded-lg border border-purple-500/30 bg-purple-500/5 hover:bg-purple-500/10 transition-all duration-300 text-left text-xs md:text-sm"
                >
                  <span className="text-purple-400">📋</span> Show me my pending tasks
                </button>
                <button
                  onClick={() => setInput("Mark task 1 as complete")}
                  className="px-3 md:px-4 py-2.5 md:py-3 rounded-lg border border-green-500/30 bg-green-500/5 hover:bg-green-500/10 transition-all duration-300 text-left text-xs md:text-sm"
                >
                  <span className="text-green-400">✅</span> Mark task 1 as complete
                </button>
                <button
                  onClick={() => setInput("Update my task with a new due date")}
                  className="px-3 md:px-4 py-2.5 md:py-3 rounded-lg border border-pink-500/30 bg-pink-500/5 hover:bg-pink-500/10 transition-all duration-300 text-left text-xs md:text-sm"
                >
                  <span className="text-pink-400">📅</span> Update my task with a new due date
                </button>
              </div>
            </div>
          ) : (
            <div className="space-y-4 max-w-4xl mx-auto">
              {messages.map((message) => (
                <ChatMessage
                  key={message.id}
                  role={message.role}
                  content={message.content}
                  timestamp={message.timestamp}
                  toolCalls={message.toolCalls}
                />
              ))}
              <div ref={messagesEndRef} />
            </div>
          )}
        </div>

        {/* ===== CHAT INPUT ===== */}
        <div className="flex-shrink-0 border-t border-gray-700/50 bg-gray-900/80 backdrop-blur-md px-3 md:px-6 py-3">
          <div className="flex items-center gap-2 md:gap-3 max-w-4xl mx-auto">
            <Input
              ref={inputRef}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Type a message..."
              disabled={isSending}
              autoFocus
              className="flex-1 h-10 md:h-11 bg-gray-800/60 border-gray-700/50 text-white placeholder-gray-500 focus:border-cyan-500/50 focus:ring-1 focus:ring-cyan-500/30 text-sm"
            />
            <Button
              onClick={sendMessage}
              disabled={isSending || !input.trim()}
              className="h-10 md:h-11 px-4 md:px-6 bg-gradient-to-r from-cyan-500 to-purple-600 hover:from-cyan-600 hover:to-purple-700 text-white transition-all duration-300"
            >
              {isSending ? (
                <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                </svg>
              ) : (
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
                </svg>
              )}
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
}
