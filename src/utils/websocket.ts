export class WebSocketService {
  private static instance: WebSocketService;
  private ws: WebSocket | null = null;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectDelay = 1000;
  private listeners: ((data: any) => void)[] = [];

  private constructor() {
    this.connect();
  }

  public static getInstance(): WebSocketService {
    if (!WebSocketService.instance) {
      WebSocketService.instance = new WebSocketService();
    }
    return WebSocketService.instance;
  }

  private connect() {
    try {
      // In a real implementation, this would connect to your WebSocket server
      console.log('WebSocket connection simulation...');
      
      // Simulate connection events
      setTimeout(() => {
        this.onOpen();
      }, 1000);

      // Simulate periodic messages
      setInterval(() => {
        this.simulateMessage();
      }, 10000);

    } catch (error) {
      console.error('WebSocket connection failed:', error);
      this.onError();
    }
  }

  private onOpen() {
    console.log('WebSocket connected (simulated)');
    this.reconnectAttempts = 0;
    
    // Notify listeners of connection
    this.notifyListeners({ type: 'connection', status: 'connected' });
  }

  private onError() {
    console.error('WebSocket error (simulated)');
    this.notifyListeners({ type: 'connection', status: 'error' });
    
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      setTimeout(() => {
        this.reconnectAttempts++;
        this.connect();
      }, this.reconnectDelay * this.reconnectAttempts);
    }
  }

  private simulateMessage() {
    const messages = [
      { type: 'sync_status', status: 'connected' },
      { type: 'device_update', device: 'Mobile Device', status: 'online' },
      { type: 'security_alert', level: 'info', message: 'New device registered' }
    ];
    
    const randomMessage = messages[Math.floor(Math.random() * messages.length)];
    this.notifyListeners(randomMessage);
  }

  public send(data: any) {
    // In a real implementation, this would send data through the WebSocket
    console.log('Sending data (simulated):', data);
    
    // Simulate server response
    setTimeout(() => {
      this.notifyListeners({
        type: 'response',
        originalData: data,
        status: 'success'
      });
    }, 500);
  }

  public addListener(callback: (data: any) => void) {
    this.listeners.push(callback);
  }

  public removeListener(callback: (data: any) => void) {
    this.listeners = this.listeners.filter(listener => listener !== callback);
  }

  private notifyListeners(data: any) {
    this.listeners.forEach(listener => {
      try {
        listener(data);
      } catch (error) {
        console.error('WebSocket listener error:', error);
      }
    });
  }

  public disconnect() {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
  }
}