class BtClients extends React.Component {
  constructor(props) {
    super(props)

    this.state = {
      clients: [],
      isLoading: false,
      error: null,
      isInitalFetch: true,
    }
  }

  componentDidMount() {
    this.fetchClients();
    this.timerID = setInterval(
      () => this.fetchClients(),
      2000
    );
  }

  componentWillUnmount() {
    clearInterval(this.timerID);
  }

  fetchClients() {
    this.setState({ isLoading: true });
    fetch(API + 'clients')
      .then(response => response.json())
      .then(
        (result) => {
          this.setState({
            clients: result.clients,
            isLoading: false,
            isInitalFetch: false,
            error: null})
        },
        (error) => {
          this.setState({
            error: 'Something went wrong during client fetch...',
            isLoading: false,
            isInitalFetch: false})
          this.props.notify(NotifyType.error, 'Something went wrong during client fetch...')
        }
      )
  }

  render() {
    const { clients, isLoading, error, isInitalFetch } = this.state;
    var clientsContent = ""

    if (error) {
      clientsContent = <ErrorAlert message={error} />;
    } else if (isLoading && isInitalFetch) {
      clientsContent = <LoadingSpinner />;
    } else {
      clientsContent = clients.map(client => (
        <BtClient key={client.address} {...client} notify={this.props.notify} />
      ));
    }
    return (
      <div className="container">
        <h1 className="text-center fw-light">Bluetooth Clients</h1>
        <div className="row">
          {clientsContent}
        </div>
      </div>
    );
  }
}

class BtClient extends React.Component {
  changeConnectState() {
    const requestOptions = {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ clientAddress: this.props.address })
    };

    var connectionApiEndpoint = ""
    if (this.props.isConnected) {
      connectionApiEndpoint = "disconnect_client"
    } else {
      connectionApiEndpoint = "connect_client"
    }

    fetch(API + connectionApiEndpoint, requestOptions)
      .then(
        (response) => {
          if(response.ok) {
            console.log("success")
            this.props.notify(NotifyType.success, 'Connection change requested successfully')
          } else {
            throw Error("")
          }
       })
      .catch((error) => {
          console.log("error")
          this.props.notify(NotifyType.error, 'Something went wrong during client connection change...')
       })
  }

  setAsActiveBtHost() {
    const requestOptions = {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ clientAddress: this.props.address })
    };

    fetch(API + "switch_active_bt_host", requestOptions)
      .then(
        (response) => {
          if(response.ok) {
            console.log("success")
            this.props.notify(NotifyType.success, 'Change active bluetooth host requested successfully')
          } else {
            throw Error("")
          }
       })
      .catch((error) => {
          console.log("error")
          this.props.notify(NotifyType.error, 'Something went wrong during client connection change...')
       })
  }

  renderSwitchActiveBtHostButton() {
    if(!this.props.isHost) {
      return (
        <button className="btn btn-outline-secondary mx-1" onClick={() => this.setAsActiveBtHost()}>
          Set as active Host
        </button>
      )
    } else {
      return
    }
  }
  renderConnectedCard() {
    var isHost = ""
    if(this.props.isHost) {
      isHost = "(active Host)"
    }
    return (
      <div className="col-md-6 ">
        <div className="card mb-3 border-success">
          <h5 className="card-header bg-success text-center text-white">{this.props.name}</h5>
          <div className="card-body">
            <h6 className="card-title">Connected {isHost}</h6>
            <p className="card-text">{this.props.address}</p>
            <div className="text-end">
              {this.renderSwitchActiveBtHostButton()}
              <button className="btn btn-outline-danger" onClick={() => this.changeConnectState()}>
                Disconnect
              </button>
            </div>
          </div>
        </div>
      </div>
    ); 
  }

  renderDisconnectedCard() {
    return (
      <div className="col-md-6 ">
        <div className="card mb-3 border-secondary">
          <h5 className="card-header bg-secondary text-center text-white">{this.props.name}</h5>
          <div className="card-body">
            <h6 className="card-title">Disconnected</h6>
            <p className="card-text">{this.props.address}</p>
            <div className="text-end">
              {this.renderSwitchActiveBtHostButton()}
              <button className="btn btn-outline-success" onClick={() => this.changeConnectState()}>
                Connect
              </button>
            </div>
          </div>
        </div>
      </div>
    ); 
  }

  render() {
    if (this.props.isConnected) {
      return (this.renderConnectedCard());
    } else {
      return (this.renderDisconnectedCard());
    }
  }
}
