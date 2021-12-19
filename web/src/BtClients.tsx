import React from 'react';
import { BtClient, BtClientInfo } from './BtClient';

type BtClientsState = {
  clients: BtClientInfo[];
  isLoading: boolean;
};

export default class BtClients extends React.Component<any, BtClientsState> {
  static MAX_TIMEOUT_CHECK_SERVER_CON = 10000;

  address = 'zimba-kvm';

  port = 8080;

  ws?: WebSocket;

  connectInterval: ReturnType<typeof setTimeout> = setTimeout(() => {});

  timeout = 250;

  constructor(props: any) {
    super(props);

    this.state = {
      clients: [],
      isLoading: false,
    };
  }

  componentDidMount() {
    this.connect();
  }

  componentWillUnmount() {
    this.ws?.close();
  }

  connect = () => {
    const webSocketAddress = `ws://${this.address}:${this.port}/bt-clients-socket`;
    // eslint-disable-next-line no-console
    console.log(`BT-Client-BE: connect to: ${webSocketAddress}`);
    this.ws = new WebSocket(webSocketAddress);

    // websocket onopen event listener
    this.ws.onopen = () => {
      // eslint-disable-next-line no-console
      console.log('BT-Client-BE: connected websocket');

      this.timeout = 250; // reset timer to 250 on open of websocket connection
      clearTimeout(this.connectInterval); // clear Interval on on open of websocket connection
    };

    // websocket onclose event listener
    this.ws.onclose = (e) => {
      // eslint-disable-next-line no-console
      console.log(
        `BT-Client-BE: Socket is closed. Reconnect will be attempted in ${Math.min(
          BtClients.MAX_TIMEOUT_CHECK_SERVER_CON / 1000,
          (this.timeout + this.timeout) / 1000
        )} second.`,
        e.reason
      );

      this.timeout += this.timeout; // increment retry interval
      this.connectInterval = setTimeout(
        this.check,
        Math.min(BtClients.MAX_TIMEOUT_CHECK_SERVER_CON, this.timeout)
      ); // call check function after timeout
    };

    // websocket onerror event listener
    this.ws.onerror = () => {
      // eslint-disable-next-line no-console
      console.error('BT-Client-BE: Socket encountered error: Closing socket');
      this.setState({
        isLoading: true,
      });
      this.ws?.close();
    };

    this.ws.onmessage = (message) => {
      const dataJson = JSON.parse(JSON.parse(message.data));
      const sortedClients = dataJson.clients.sort(
        (a: BtClientInfo, b: BtClientInfo) => a.order - b.order
      );
      this.setState({
        clients: sortedClients,
        isLoading: false,
      });
    };
  };

  check = () => {
    if (!this.ws || this.ws.readyState === WebSocket.CLOSED) this.connect(); // check if websocket instance is closed, if so call `connect` function.
  };

  render() {
    const { clients, isLoading } = this.state;
    let clientsContent = <></>;

    if (isLoading) {
      clientsContent = (
        <div className="d-flex justify-content-center py-5">
          <div className="spinner-border text-secondary" role="status">
            <span className="visually-hidden">Loading...</span>
          </div>
        </div>
      );
    } else if (clients) {
      let lastClientOrderNumber = 0;
      clients.forEach((client) => {
        if (client.order > lastClientOrderNumber) {
          lastClientOrderNumber = client.order;
        }
      });
      const clientsInfo = clients.map((client) => (
        <BtClient
          key={client.address}
          client={client}
          lastClientOrderNumber={lastClientOrderNumber}
        />
      ));
      clientsContent = <>{clientsInfo}</>;
    }
    return (
      <div className="container py-2">
        <h1 className="text-center py-4 fw-light">Bluetooth Clients</h1>
        <div className="row">{clientsContent}</div>
      </div>
    );
  }
}
