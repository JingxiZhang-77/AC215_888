export default function Footer() {
  const currentYear = new Date().getFullYear();

  return (
    <footer className="border-t bg-muted/50">
      <div className="container mx-auto px-4 py-6">
        <div className="flex flex-col md:flex-row items-center justify-between gap-4">
          <p className="text-sm text-muted-foreground">
            © {currentYear} Safety Event Classification System. Powered by Google Gemini AI.
          </p>
          <div className="flex items-center gap-4 text-sm text-muted-foreground">
            <span>5 Departments</span>
            <span>•</span>
            <span>5 Languages</span>
            <span>•</span>
            <span>4 Classification Codes</span>
          </div>
        </div>
      </div>
    </footer>
  );
}
