import React from 'react';
import { Row, Col } from 'react-bootstrap';
import { ServerConfig, InfoBanner, WelcomeBanner } from './Common';
import UpdatePerformer from './UpdatePerformer';
import { NotificationContext, NotifyType } from './Notifications';

type KeyboardCodes = {
  keyCodes: { [key: string]: number };
  modifierKeys: { [key: string]: number };
};

type SettingsState = {
  settings: {
    web: { port: string };
    hotkeys: {nextHost: [[boolean, boolean, boolean, boolean, boolean, boolean, boolean, boolean], number, number, number, number, number, number]}
  };
  keyboardCodes: KeyboardCodes
};

export default class Settings extends React.Component<any, SettingsState> {

  static contextType = NotificationContext;

  constructor(props: any) {
    super(props)

    this.state = {
      settings: {
        web: {
          port: "8080"
        },
        hotkeys: {
          nextHost: [[false, false, false, false, false, false, false, false], 0, 0, 0, 0, 0, 0]
        },
      },
      keyboardCodes: {
        keyCodes: {},
        modifierKeys: {},
      },
    }
  }

  componentDidMount() {
    this.fetchSettings();
    this.fetchKeyboardCods();
  }

  fetchSettings() {
    fetch(ServerConfig.url + 'get_settings')
      .then(response => response.json())
      .then(
        (result) => {
          this.setState({
            settings: result.settings})
        },
        (error) => {
          this.context.addNotification(NotifyType.error, 'Something went wrong during settings fetch...')
        }
      )
  }

  fetchKeyboardCods() {
    fetch(ServerConfig.url + 'get_keyboard_codes')
      .then(response => response.json())
      .then(
        (result) => {
          this.setState({
            keyboardCodes: result.keyboardCodes})
        },
        (error) => {
          this.context.addNotification(NotifyType.error, 'Something went wrong during keyboard codes fetch...')
        }
      )
  }

  sendSettings() {
    const requestOptions = {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ settings: this.state.settings })
    };

    fetch(ServerConfig.url + "set_settings", requestOptions)
      .then(
        (response) => {
          if(response.ok) {
            this.context.addNotification(NotifyType.success, 'Applying settings requested successfully')
          } else {
            throw Error("")
          }
       })
      .catch((error) => {
          console.log("error")
          this.context.addNotification(NotifyType.error, 'Something went wrong during settings send...')
       })
  }

  handleWebPortChange(event: React.ChangeEvent<HTMLInputElement>) {
    const { settings } = this.state;

    switch (event.target.id) {
      case "webPort":
        settings.web.port = event.target.value
        break;
      default:
        break;
    }
    this.setState({settings: settings})
  }

  handleHotkeyChange(event: React.ChangeEvent<HTMLSelectElement>) {
    const { settings } = this.state;

    switch (event.target.id) {
      case "hotkeyNextHostKey1":
        settings.hotkeys.nextHost[1] = parseInt(event.target.value, 10)
        break;
      default:
        break;
    }
    this.setState({settings: settings})
  }

  handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    this.sendSettings()
    event.preventDefault();
  }

  renderWebSection() {
    return (
      <Row className="g-3 align-items-center">
        <h2 className="fw-light">Web Settings</h2>
          <InfoBanner message="Web setting changes take effect after web service restart." />
          <label htmlFor="webPort" className="col-sm-3 col-form-label">Port Number:</label>
          <Col sm={9}>
            <input type="number" id="webPort" className="form-control" value={this.state.settings.web.port} onChange={this.handleWebPortChange.bind(this)}/>
          </Col>
      </Row>
    );
  }

  renderHotkeySection(keyboardCodes: KeyboardCodes) {
    let keyCodesSelectContent = Object.entries(keyboardCodes.keyCodes).map(([key, value]) => (
      <option key={key} value={value}>{key}</option>
    ));
    return (
      <div className="row g-3 mt-5 align-items-center">
        <h2 className="fw-light">Hotkey Settings</h2>
          <p>Configure your hotkeys to perform K(V)M actions via the connected keyboard.</p>
          <label htmlFor="hotkeyNextHostKey1" className="col-sm-4 col-form-label">Next Host Hotkey:</label>
          <div className="col-sm-8">
            <select className="form-select" id="hotkeyNextHostKey1" value={this.state.settings.hotkeys.nextHost[1]} onChange={this.handleHotkeyChange.bind(this)}>
              {keyCodesSelectContent}
            </select>
          </div>
      </div>
    );
  }

  render() {
    const { keyboardCodes } = this.state;
    return (
      <section id="settings">
        <WelcomeBanner name="Settings" message="Configure your RPI-K(V)M" />
        <UpdatePerformer/>
        <div className="container mt-5">
          <form onSubmit={this.handleSubmit.bind(this)}>
            {this.renderWebSection()}
            {this.renderHotkeySection(keyboardCodes)}
            <div className="row mt-3">
              <div className="d-grid col-4">
                <input type="submit" className="btn btn-outline-primary" value="Apply"/>
              </div>
            </div>
          </form>
        </div>
        <div className="container my-5">
          <ServiceRestartSection />
        </div>
      </section>
    );
  }
}

class ServiceRestartSection extends React.Component {

  static contextType = NotificationContext;

  sendServiceRestart(serviceName: string) {
    const requestOptions = {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ service: serviceName })
    };

    fetch(ServerConfig.url + "restart_service", requestOptions)
      .then(
        (response) => {
          if(response.ok) {
            this.context.addNotification(NotifyType.success, 'Restart ' + serviceName + ' service requested successfully')
          } else {
            this.context.addNotification(NotifyType.error, 'Something went wrong during restart ' + serviceName + ' service send...')
          }
       })
      .catch((error) => {
          this.context.addNotification(NotifyType.error, 'Something went wrong during restart ' + serviceName + ' service send...')
       })
  }

  render() {
    return (
      <div className="row g-3 align-items-center">
        <h2 className="fw-light">RPI-K(V)M Service Actions</h2>

        <div className="d-grid col-3">
          <button className="btn btn-outline-danger" onClick={() => this.sendServiceRestart("info-hub")}>
            Restart Info Hub
          </button>
        </div>

        <div className="d-grid col-3">
          <button className="btn btn-outline-danger" onClick={() => this.sendServiceRestart("web")}>
            Restart Web service
          </button>
        </div>

        <div className="d-grid col-3">
          <button className="btn btn-outline-danger" onClick={() => this.sendServiceRestart("kvm")}>
            Restart KVM service
          </button>
        </div>

        <div className="d-grid col-3">
          <button className="btn btn-outline-danger" onClick={() => this.sendServiceRestart("rpi")}>
            Restart Raspberry Pi
          </button>
        </div>
      </div>
    );
  }
}
