import { render, screen } from "@testing-library/react";

import Home from "@/app/page";

describe("Home page", () => {
  it("renders dashboard title", () => {
    render(<Home />);
    expect(screen.getByText("Toshokan Dashboard")).toBeInTheDocument();
  });
});
