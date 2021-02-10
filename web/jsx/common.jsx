const API = '/'

class InfoBanner extends React.Component {
  render() {
    return (
      <div className="alert alert-primary" role="alert">
        {this.props.message}
      </div>
    );
  }
}

class ErrorAlert extends React.Component {
  render() {
    return (
      <div className="alert alert-danger" role="alert">
        {this.props.message}
      </div>
    );
  }
}

class WelcomeBanner extends React.Component {
  render() {
    return (
      <div className="py-5 text-center container">
        <div className="row py-lg-5">
          <div className="col-lg-6 col-md-8 mx-auto">
            <h1 className="fw-light">{this.props.name}</h1>
            <p className="lead text-muted">{this.props.message}</p>
          </div>
        </div>
      </div>
    );
  }
}

class LoadingSpinner extends React.Component {
  render() {
    return (
      <div className="d-flex justify-content-center">
        <div className="spinner-border text-secondary" role="status">
          <span className="visually-hidden">Loading...</span>
        </div>
      </div>
    );
  }
}
