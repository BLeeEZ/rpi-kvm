const NotifyType = Object.freeze({"error": 1, "success": 2, "info": 3})

class Notifier extends React.Component {
  constructor(props) {
    super(props)
  }

  render() {
    var notificationsContent = this.props.notifications.map(notification => (
      <Notification key={notification.id} {...notification} clearNotification={this.props.clearNotification}/>
    ));

    return (
      <div aria-live="polite" aria-atomic="true" className="position-relative" style={{"zIndex": 999}}>
        <div className="toast-container position-absolute top-0 end-0 p-3">
          {notificationsContent}
        </div>
      </div>
    );
  }
}

class Notification extends React.Component {
  render() {
    var toastHeader = ""
    var toastTitle = ""
    if(this.props.type == NotifyType.success) {
      toastHeader = "toast-header bg-success text-white"
      toastTitle = "Success"
    } else if(this.props.type == NotifyType.info) {
      toastHeader = "toast-header bg-primary text-white"
      toastTitle = "Info"
    } else { //else and error
      toastHeader = "toast-header bg-danger text-white"
      toastTitle = "Error"
    }

    return (
      <div className="toast show" role="alert" aria-live="assertive" aria-atomic="true">
        <div className={toastHeader} >
          <strong className="me-auto">{toastTitle}</strong>
          <button type="button" className="btn-close" onClick={() => this.props.clearNotification(this.props.id)}></button>
        </div>
        <div className="toast-body">
          {this.props.msg}
        </div>
      </div>
    );
  }
}

