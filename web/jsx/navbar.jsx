class Navbar extends React.Component {
  renderViewLinks(viewType) {
    var linkClassNames = ""
    if(viewType == this.props.activeView) {
      linkClassNames = "nav-link active"
    } else {
      linkClassNames = "nav-link"
    }

    var linkName = ""
    switch (viewType) {
      case ViewType.main:
        linkName = "Home"
        break;
      case ViewType.settings:
        linkName = "Settings"
        break;
      default:
         linkName = "Home"
         break;
    }

    return (
      <a className={linkClassNames} href="#0" onClick={() => this.props.switchActiveView(viewType)}>{linkName}</a>
    );
  }

  render() {
    return (
      <nav className="navbar navbar-expand-lg navbar-light bg-light">
        <div className="container-fluid">
          <a className="navbar-brand" href="#">RPI-K(V)M</a>
          <button className="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNavAltMarkup" aria-controls="navbarNavAltMarkup" aria-expanded="false" aria-label="Toggle navigation">
            <span className="navbar-toggler-icon"></span>
          </button>
          <div className="collapse navbar-collapse" id="navbarNavAltMarkup">
            <div className="navbar-nav">
              {this.renderViewLinks(ViewType.main)}
              {this.renderViewLinks(ViewType.settings)}
            </div>
          </div>
        </div>
      </nav>
    );
  }
}

