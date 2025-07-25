class MockEventSource extends EventTarget {
  constructor(url) {
    super();
    this.url = url;
    this.current = 0;
    this.total = 10;

    this.interval = setInterval(() => {
      if (this.current >= this.total) {
        this.close();
        return;
      }

      this.current++;

      const fakeData = {
        status: Math.random() > 0.2 ? 'success' : 'error',
        error_message: 'Simulated error',
        current: this.current,
        total: this.total,
        contact_name: `Test User ${this.current}`,
        contact_phone: '+123456789',
        instance_name: 'FakeInstance'
      };

      const event = new MessageEvent('message', {
        data: JSON.stringify(fakeData)
      });

      if (typeof this.onmessage === 'function') {
        this.onmessage(event);
      }

      this.dispatchEvent(event);
    }, 800);
  }

  close() {
    clearInterval(this.interval);
  }
}
