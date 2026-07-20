import { Link } from "react-router-dom";

export function Brand() {
  return <Link className="brand" to="/" aria-label="InsightFlow home">
    <span className="brand-bars" aria-hidden="true"><i/><i/><i/><i/></span>
    <strong>InsightFlow</strong>
  </Link>;
}
