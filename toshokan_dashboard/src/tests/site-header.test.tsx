import { render, screen } from "@testing-library/react";

import SiteHeader from "@/components/site-header";

describe("SiteHeader", () => {
  it("renders navigation links", () => {
    render(<SiteHeader />);
    expect(screen.getByText("Identity")).toBeInTheDocument();
    expect(screen.getByText("Dashboard")).toBeInTheDocument();
    expect(screen.getByText("Dictionary")).toBeInTheDocument();
  });
});
