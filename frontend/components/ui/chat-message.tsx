'use client';

import { cn } from '@/lib/utils';

interface ChatMessageProps {
  role: 'user' | 'assistant';
  content: string;
  timestamp?: string;
  toolCalls?: Array<{
    tool_name: string;
    status: string;
  }>;
}

export function ChatMessage({ role, content, timestamp, toolCalls }: ChatMessageProps) {
  const isUser = role === 'user';

  return (
    <div className={cn(
      "flex w-full mb-4",
      isUser ? "justify-end" : "justify-start"
    )}>
      <div className={cn(
        "max-w-[80%] rounded-lg p-4 shadow-lg",
        isUser 
          ? "bg-gradient-to-r from-cyan-500 to-blue-600 text-white"
          : "bg-gradient-to-r from-gray-800 to-gray-900 text-gray-100 border border-purple-500/30"
      )}>
        <div className="flex items-start space-x-2">
          <div className="flex-1">
            <div className="flex items-center space-x-2 mb-2">
              <span className="text-xs font-semibold opacity-80">
                {isUser ? 'You' : 'AI Assistant'}
              </span>
              {timestamp && (
                <span className="text-xs opacity-60">
                  {new Date(timestamp).toLocaleTimeString()}
                </span>
              )}
            </div>
            <p className="text-sm whitespace-pre-wrap break-words">{content}</p>
            
            {toolCalls && toolCalls.length > 0 && (
              <div className="mt-3 pt-3 border-t border-purple-500/20">
                <p className="text-xs font-semibold mb-2 opacity-80">Tool Actions:</p>
                <div className="space-y-1">
                  {toolCalls.map((tool, idx) => (
                    <div key={idx} className="flex items-center space-x-2 text-xs">
                      <span className={cn(
                        "w-2 h-2 rounded-full",
                        tool.status === 'success' ? 'bg-green-400' : 'bg-red-400'
                      )}></span>
                      <span className="opacity-80">{tool.tool_name}</span>
                      <span className={cn(
                        "text-xs",
                        tool.status === 'success' ? 'text-green-400' : 'text-red-400'
                      )}>
                        {tool.status}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
