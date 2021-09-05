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
          var sorted_clients = result.clients.sort((a, b) => a.order - b.order)
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
      var lastClientOrderNumber = 0;
      for (const [index, client] of clients.entries()) {
        if (client.order > lastClientOrderNumber) {
          lastClientOrderNumber = client.order
        }
      };
      clientsContent = clients.map(client => (
        <BtClient key={client.address} {...client} lastClientOrderNumber={lastClientOrderNumber} notify={this.props.notify} />
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

  removeClient() {
    const requestOptions = {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ clientAddress: this.props.address })
    };

    fetch(API + "remove_client", requestOptions)
      .then(
        (response) => {
          if(response.ok) {
            console.log("success")
            this.props.notify(NotifyType.success, 'Remove client requested successfully')
          } else {
            throw Error("")
          }
       })
      .catch((error) => {
          console.log("error")
          this.props.notify(NotifyType.error, 'Something went wrong during client removal...')
       })
  }

  changeOrderLower() {
    const requestOptions = {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ 
        clientAddress: this.props.address,
        order_type: "lower"
      })
    };

    fetch(API + "change_client_order", requestOptions)
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

  changeOrderHigher() {
    const requestOptions = {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ 
        clientAddress: this.props.address,
        order_type: "higher"
      })
    };

    fetch(API + "change_client_order", requestOptions)
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

  renderOrderLowerButton() {
    if(this.props.order > 0) {
      return (
        <button className="btn btn-default text-white col-1 py-0 ps-0 pe-3" onClick={() => this.changeOrderLower()}> <i className="bi bi-chevron-left" style={{'fontsize': '0.9rem'}}></i> </button>
      )
    } else {
      return (
        <button className="btn btn-default text-white col-1 py-0 ps-0 pe-3 disabled" onClick={() => this.changeOrderLower()}> <i className="bi bi-chevron-left" style={{'fontsize': '0.9rem'}}></i> </button>
      )
    }
  }

  renderOrderHigherButton() {
    if(this.props.order < this.props.lastClientOrderNumber) {
      return (
        <button className="btn btn-default text-white col-1 py-0 ps-0 pe-3" onClick={() => this.changeOrderHigher()}> <i className="bi bi-chevron-right" style={{'fontsize': '0.9rem'}}></i> </button>
      )
    } else {
      return (
        <button className="btn btn-default text-white col-1 py-0 ps-0 pe-3 disabled" onClick={() => this.changeOrderHigher()}> <i className="bi bi-chevron-right" style={{'fontsize': '0.9rem'}}></i> </button>
      )
    }
  }
  
  renderOrderButtons() {
    return (
      <div className="row">
        {this.renderOrderLowerButton()}
        {this.renderOrderHigherButton()}
      </div>
    )
  }

  renderConnectedCard() {
    var isHost = ""
    if(this.props.isHost) {
      isHost = "(active Host)"
    }
    return (
      <div className="col-md-6 ">
        <div className="card mb-3 border-success">
          <div className="card-header bg-success pb-0">
            <div className="row">
              <div className="text-center text-white col-2">
                {this.renderOrderButtons()}
              </div>
              <h5 className="text-center text-white col-8">
                {this.props.name}
              </h5>
            </div>
          </div>
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
          <div className="card-header bg-secondary pb-0">
            <div className="row">
              <div className="text-center text-white col-2">
                {this.renderOrderButtons()}
              </div>
              <h5 className="text-center text-white col-8">
                {this.props.name}
              </h5>
              <div className="text-center text-white col-1 offset-1">
                <ClientRemovalModalButton {...this.props} removeCB={() => this.removeClient()}/>
              </div>
            </div>
          </div>
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
