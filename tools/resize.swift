// Resize a photo for the web, applying its camera rotation (sips does not).
// usage: swift tools/resize.swift in.jpg out.jpg maxLongEdge quality
// Prints "width height" of the result.
import Foundation
import CoreGraphics
import ImageIO
import UniformTypeIdentifiers

let a = CommandLine.arguments
guard a.count == 5, let src = CGImageSourceCreateWithURL(URL(fileURLWithPath: a[1]) as CFURL, nil) else {
    FileHandle.standardError.write("usage: resize.swift in out maxLongEdge quality\n".data(using: .utf8)!); exit(1)
}
let opts: [CFString: Any] = [kCGImageSourceCreateThumbnailFromImageAlways: true,
                             kCGImageSourceCreateThumbnailWithTransform: true,
                             kCGImageSourceThumbnailMaxPixelSize: Int(a[3])!]
let img = CGImageSourceCreateThumbnailAtIndex(src, 0, opts as CFDictionary)!
let dest = CGImageDestinationCreateWithURL(URL(fileURLWithPath: a[2]) as CFURL, UTType.jpeg.identifier as CFString, 1, nil)!
CGImageDestinationAddImage(dest, img, [kCGImageDestinationLossyCompressionQuality: Double(a[4])!] as CFDictionary)
CGImageDestinationFinalize(dest)
print(img.width, img.height)
