import ArxivSwift

// Create a client
let client = ArxivClient()

// Simple search
do {
    let entries = try await client.searchByTitle("spintronics", maxResults: 5)
    for entry in entries {
        print("\(entry.title) by \(entry.formattedAuthors), available at \(entry.links.first?.href ?? "N/A")")
    }
} catch {
    print("Error: \(error)")
}
