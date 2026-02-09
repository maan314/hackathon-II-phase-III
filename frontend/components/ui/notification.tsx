import { useState, useEffect } from 'react';
import { X } from 'lucide-react';

interface NotificationProps {
  message: string;
  type?: 'success' | 'error' | 'info' | 'warning';
  duration?: number;
  onClose?: () => void;
}

export default function Notification({ message, type = 'info', duration = 5000, onClose }: NotificationProps) {
  const [visible, setVisible] = useState(true);

  useEffect(() => {
    if (duration > 0) {
      const timer = setTimeout(() => {
        handleClose();
      }, duration);

      return () => clearTimeout(timer);
    }
  }, [duration]);

  const handleClose = () => {
    setVisible(false);
    if (onClose) {
      onClose();
    }
  };

  if (!visible) return null;

  const bgColor = {
    success: 'bg-green-900/80 border-green-500 text-green-200',
    error: 'bg-red-900/80 border-red-500 text-red-200',
    info: 'bg-blue-900/80 border-blue-500 text-blue-200',
    warning: 'bg-yellow-900/80 border-yellow-500 text-yellow-200',
  }[type];

  return (
    <div className={`fixed top-4 right-4 z-50 border px-4 py-3 rounded shadow-lg max-w-md backdrop-blur-sm ${bgColor}`}>
      <div className="flex items-start">
        <div className="flex-1">{message}</div>
        <button
          onClick={handleClose}
          className="ml-2 text-current opacity-70 hover:opacity-100"
          aria-label="Close"
        >
          <X size={20} />
        </button>
      </div>
    </div>
  );
}