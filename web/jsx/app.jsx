const ViewType = Object.freeze({"main": 1, "settings": 2})

class Application extends React.Component {
  constructor(props) {
    super(props)

    this.state = {
      notifications: [],
      activeView: ViewType.main,
    }

    this.maxNotificationCount = 6
    this.notificationAliveTime = 10 //Seconds
  }

  notify(type, msg) {
    var notification = {id: Math.random().toString(16), type: type, msg: msg, time: 0};

    var notificationsCopy = this.state.notifications.slice()
    notificationsCopy.push(notification)
    if(notificationsCopy.length > this.maxNotificationCount) {
      notificationsCopy.splice(0, 1)
    }
    this.setState({ notifications: notificationsCopy})
  }

  clearNotification(id) {
    var notificationsCopy = this.state.notifications.slice()
    const index = notificationsCopy.findIndex(element => element.id == id)
    if(index > -1) {
      notificationsCopy.splice(index, 1)
    }
    this.setState({ notifications: notificationsCopy})
  }

  updateNotifications() {
    var notificationsCopy = this.state.notifications.slice()
    var notificationsCleared = []
    notificationsCopy.forEach(element => {
      element.time += 1
      if(element.time < this.notificationAliveTime) {
        notificationsCleared.push(element)
      }
    })
    this.setState({ notifications: notificationsCleared})
  }

  componentDidMount() {
    this.timerID = setInterval(
      () => this.updateNotifications(),
      1000
    );
  }

  componentWillUnmount() {
    clearInterval(this.timerID);
  }

  switchActiveView(newActiveView) {
      this.setState({activeView: newActiveView})
  }

  renderSettingsView() {
      return (
        <SettingsView notify={(type, msg) => this.notify(type, msg)}/>
      );
  }

  renderMainView() {
      return (
        <MainView notify={(type, msg) => this.notify(type, msg)}/>
      );
  }

  renderActiveView() {
      if(this.state.activeView == ViewType.settings) {
          return this.renderSettingsView()
      } else { // main and everything else
          return this.renderMainView()
      }
  }

  render() {
    return (
      <div id="app">
        <div id="header">
          <Navbar activeView={this.state.activeView} switchActiveView={(newActiveView) => this.switchActiveView(newActiveView)} />
        </div>
        <Notifier notifications={this.state.notifications} clearNotification={(id) => this.clearNotification(id)}/>
        {this.renderActiveView()}
      </div>
    );
  }
}

