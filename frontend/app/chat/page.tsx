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
      <div className="container mx-auto px-4 py-8 h-screen flex flex-col">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h1 className="text-4xl font-bold bg-gradient-to-r from-cyan-400 via-purple-500 to-pink-500 bg-clip-text text-transparent">
              AI Assistant
            </h1>
            <p className="text-gray-400 mt-2">Chat with your AI-powered task assistant</p>
          </div>
          <div className="flex items-center space-x-4">
            <Button
              onClick={startNewConversation}
              variant="outline"
              className="border-purple-500 text-purple-400 hover:bg-purple-500 hover:text-gray-900 transition-all duration-300"
            >
              New Chat
            </Button>
            <Link href="/dashboard">
              <Button
                variant="outline"
                className="border-cyan-500 text-cyan-400 hover:bg-cyan-500 hover:text-gray-900 transition-all duration-300"
              >
                Dashboard
              </Button>
            </Link>
          </div>
        </div>

        <div className="flex-1 overflow-y-auto mb-6 rounded-xl border border-purple-500/30 bg-gradient-to-br from-gray-800/50 to-gray-900/50 backdrop-blur-sm p-6 shadow-xl">
          {messages.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-full text-center">
              <div className="w-20 h-20 rounded-full bg-gradient-to-r from-cyan-500 to-purple-600 flex items-center justify-center mb-6">
                <svg className="w-10 h-10" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
                </svg>
              </div>
              <h2 className="text-2xl font-bold mb-4 bg-gradient-to-r from-cyan-400 to-purple-500 bg-clip-text text-transparent">
                Start a Conversation
              </h2>
              <p className="text-gray-400 mb-6 max-w-md">
                Ask me to help you manage your tasks, create new todos, mark tasks as complete, or get information about your task list.
              </p>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3 max-w-2xl">
                <button
                  onClick={() => setInput("Create a task to review the proposal")}
                  className="px-4 py-3 rounded-lg border border-cyan-500/30 bg-cyan-500/5 hover:bg-cyan-500/10 transition-all duration-300 text-left text-sm"
                >
                  <span className="text-cyan-400">💡</span> Create a task to review the proposal
                </button>
                <button
                  onClick={() => setInput("Show me my pending tasks")}
                  className="px-4 py-3 rounded-lg border border-purple-500/30 bg-purple-500/5 hover:bg-purple-500/10 transition-all duration-300 text-left text-sm"
                >
                  <span className="text-purple-400">📋</span> Show me my pending tasks
                </button>
                <button
                  onClick={() => setInput("Mark task 1 as complete")}
                  className="px-4 py-3 rounded-lg border border-green-500/30 bg-green-500/5 hover:bg-green-500/10 transition-all duration-300 text-left text-sm"
                >
                  <span className="text-green-400">✅</span> Mark task 1 as complete
                </button>
                <button
                  onClick={() => setInput("Update my task with a new due date")}
                  className="px-4 py-3 rounded-lg border border-pink-500/30 bg-pink-500/5 hover:bg-pink-500/10 transition-all duration-300 text-left text-sm"
                >
                  <span className="text-pink-400">📅</span> Update my task with a new due date
                </button>
              </div>
            </div>
          ) : (
            <div className="space-y-4">
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

        <div className="flex items-center space-x-4">
          <Input
            ref={inputRef}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Type your message... (Press Enter to send)"
            disabled={isSending}
            autoFocus
            className="flex-1 bg-gray-800 border-purple-500/30 text-white placeholder-gray-500 focus:border-cyan-500 focus:ring-cyan-500"
          />
          <Button
            onClick={sendMessage}
            disabled={isSending || !input.trim()}
            className="bg-gradient-to-r from-cyan-500 to-purple-600 hover:from-cyan-600 hover:to-purple-700 text-white px-8 transition-all duration-300 shadow-lg hover:shadow-cyan-500/50"
          >
            {isSending ? (
              <span className="flex items-center space-x-2">
                <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                </svg>
                <span>Sending...</span>
              </span>
            ) : (
              'Send'
            )}
          </Button>
        </div>
      </div>
    </div>
  );
}
