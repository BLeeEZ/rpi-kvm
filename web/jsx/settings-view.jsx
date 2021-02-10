class SettingsView extends React.Component {
  constructor(props) {
    super(props)

    this.handleChange = this.handleChange.bind(this);
    this.handleSubmit = this.handleSubmit.bind(this);
    
    this.state = {
      settings: {
        web: {
          port: 8080
        },
      },
    }
  }

  componentDidMount() {
    this.fetchSettings();
  }

  fetchSettings() {
    fetch(API + 'get_settings')
      .then(response => response.json())
      .then(
        (result) => {
          this.setState({
            settings: result.settings})
        },
        (error) => {
          this.props.notify(NotifyType.error, 'Something went wrong during settings fetch...')
        }
      )
  }

  sendSettings() {
    const requestOptions = {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ settings: this.state.settings })
    };

    fetch(API + "set_settings", requestOptions)
      .then(
        (response) => {
          if(response.ok) {
            console.log("success")
            this.props.notify(NotifyType.success, 'Applying settings requested successfully')
          } else {
            throw Error("")
          }
       })
      .catch((error) => {
          console.log("error")
          this.props.notify(NotifyType.error, 'Something went wrong during settings send...')
       })
  }

  handleChange(event) {
    let settings = Object.assign({}, this.state.settings);

    switch (event.target.id) {
      case "webPort":
        settings.web.port = event.target.value
        break;
      default:
        break;
    }
    this.setState({settings: settings})
  }

  handleSubmit(event) {
    this.sendSettings()
    event.preventDefault();
  }

  renderWebSection() {
    return (
      <div className="row g-3 align-items-center">
        <h2 className="fw-light">Web Settings</h2>
          <InfoBanner message="Web setting changes take effect after web service restart." />
          <label htmlFor="webPort" className="col-sm-2 col-form-label">Port Number</label>
          <div className="col-sm-10">
            <input type="number" id="webPort" className="form-control" value={this.state.settings.web.port} onChange={this.handleChange}/>
          </div>
      </div>
    );
  }

  render() {
    return (
      <section id="settings">
        <WelcomeBanner name="Settings" message="Configure your RPI-K(V)M" />
        <div className="container">
          <form onSubmit={this.handleSubmit}>
            {this.renderWebSection()}
            <div className="row mt-3">
              <div className="d-grid col-4">
                <input type="submit" className="btn btn-outline-primary" value="Apply"/>
              </div>
            </div>
          </form>
        </div>
        <div className="container mt-5">
          <ServiceRestartSection notify={this.props.notify} />
        </div>
      </section>
    );
  }
}

class ServiceRestartSection extends React.Component {
  sendServiceRestart(serviceName) {
    const requestOptions = {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ service: serviceName })
    };

    fetch(API + "restart_service", requestOptions)
      .then(
        (response) => {
          if(response.ok) {
            this.props.notify(NotifyType.success, 'Restart ' + serviceName + ' service requested successfully')
          } else {
            throw Error("")
          }
       })
      .catch((error) => {
          this.props.notify(NotifyType.error, 'Something went wrong during restart ' + serviceName + ' service send...')
       })
  }

  render() {
    return (
      <div className="row g-3 align-items-center">
        <h2 className="fw-light">RPI-K(V)M Service Actions</h2>

        <div className="d-grid col-4">
          <button className="btn btn-outline-danger" onClick={() => this.sendServiceRestart("web")}>
            Restart Web service
          </button>
        </div>

        <div className="d-grid col-4">
          <button className="btn btn-outline-danger" onClick={() => this.sendServiceRestart("kvm")}>
            Restart KVM service
          </button>
        </div>

        <div className="d-grid col-4">
          <button className="btn btn-outline-danger" onClick={() => this.sendServiceRestart("rpi")}>
            Restart Raspberry Pi
          </button>
        </div>
      </div>
    );
  }
}
