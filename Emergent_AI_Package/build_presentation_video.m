#import <Foundation/Foundation.h>
#import <AVFoundation/AVFoundation.h>
#import <CoreVideo/CoreVideo.h>
#import <CoreMedia/CoreMedia.h>
#import <Cocoa/Cocoa.h>

void drawCodeSlide(NSString *title, NSString *subtitle, NSString *codeSnippet, NSString *whyNote, NSString *outPath) {
    NSSize size = NSMakeSize(1920, 1080);
    NSImage *image = [[NSImage alloc] initWithSize:size];
    [image lockFocus];
    
    // Background gradient
    [[NSColor colorWithCalibratedRed:0.04 green:0.06 blue:0.10 alpha:1.0] setFill];
    NSRectFill(NSMakeRect(0, 0, size.width, size.height));
    
    // Top Banner
    [[NSColor colorWithCalibratedRed:0.08 green:0.12 blue:0.20 alpha:1.0] setFill];
    NSRectFill(NSMakeRect(0, 960, size.width, 120));
    
    // Section Pill Badge
    NSRect badgeRect = NSMakeRect(80, 995, 260, 48);
    NSBezierPath *badgePath = [NSBezierPath bezierPathWithRoundedRect:badgeRect xRadius:8 yRadius:8];
    [[NSColor colorWithCalibratedRed:0.15 green:0.45 blue:0.90 alpha:1.0] setFill];
    [badgePath fill];
    
    NSDictionary *badgeAttr = @{
        NSFontAttributeName: [NSFont boldSystemFontOfSize:22],
        NSForegroundColorAttributeName: [NSColor whiteColor]
    };
    [@"PART 2: CODE EXPLANATION" drawAtPoint:NSMakePoint(95, 1007) withAttributes:badgeAttr];
    
    // Title
    NSDictionary *titleAttr = @{
        NSFontAttributeName: [NSFont boldSystemFontOfSize:40],
        NSForegroundColorAttributeName: [NSColor whiteColor]
    };
    [title drawAtPoint:NSMakePoint(365, 1000) withAttributes:titleAttr];
    
    // Subtitle / Concept
    NSDictionary *subAttr = @{
        NSFontAttributeName: [NSFont systemFontOfSize:26],
        NSForegroundColorAttributeName: [NSColor colorWithCalibratedRed:0.6 green:0.75 blue:0.95 alpha:1.0]
    };
    [subtitle drawAtPoint:NSMakePoint(80, 905) withAttributes:subAttr];
    
    // Code Card Box
    NSRect codeBox = NSMakeRect(80, 260, 1760, 620);
    NSBezierPath *codePath = [NSBezierPath bezierPathWithRoundedRect:codeBox xRadius:16 yRadius:16];
    [[NSColor colorWithCalibratedRed:0.08 green:0.10 blue:0.15 alpha:1.0] setFill];
    [codePath fill];
    [[NSColor colorWithCalibratedRed:0.20 green:0.28 blue:0.40 alpha:1.0] setStroke];
    [codePath setLineWidth:2.0];
    [codePath stroke];
    
    // Code text
    NSMutableParagraphStyle *style = [[NSMutableParagraphStyle alloc] init];
    style.lineSpacing = 6;
    NSDictionary *codeAttr = @{
        NSFontAttributeName: [NSFont fontWithName:@"Menlo" size:24] ?: [NSFont monospacedSystemFontOfSize:24 weight:NSFontWeightRegular],
        NSForegroundColorAttributeName: [NSColor colorWithCalibratedRed:0.85 green:0.92 blue:1.0 alpha:1.0],
        NSParagraphStyleAttributeName: style
    };
    [codeSnippet drawInRect:NSMakeRect(110, 280, 1700, 570) withAttributes:codeAttr];
    
    // Why Card Box (Footer)
    NSRect whyBox = NSMakeRect(80, 60, 1760, 160);
    NSBezierPath *whyPath = [NSBezierPath bezierPathWithRoundedRect:whyBox xRadius:12 yRadius:12];
    [[NSColor colorWithCalibratedRed:0.10 green:0.15 blue:0.25 alpha:1.0] setFill];
    [whyPath fill];
    [[NSColor colorWithCalibratedRed:0.25 green:0.55 blue:0.95 alpha:1.0] setStroke];
    [whyPath setLineWidth:1.5];
    [whyPath stroke];
    
    NSDictionary *whyTitleAttr = @{
        NSFontAttributeName: [NSFont boldSystemFontOfSize:24],
        NSForegroundColorAttributeName: [NSColor colorWithCalibratedRed:0.35 green:0.75 blue:1.0 alpha:1.0]
    };
    [@"💡 WHY IT IS WRITTEN THIS WAY:" drawAtPoint:NSMakePoint(110, 170) withAttributes:whyTitleAttr];
    
    NSDictionary *whyBodyAttr = @{
        NSFontAttributeName: [NSFont systemFontOfSize:22],
        NSForegroundColorAttributeName: [NSColor colorWithCalibratedRed:0.9 green:0.92 blue:0.95 alpha:1.0]
    };
    [whyNote drawInRect:NSMakeRect(110, 80, 1700, 85) withAttributes:whyBodyAttr];
    
    [image unlockFocus];
    
    NSBitmapImageRep *rep = [[NSBitmapImageRep alloc] initWithData:[image TIFFRepresentation]];
    NSData *png = [rep representationUsingType:NSBitmapImageFileTypePNG properties:@{}];
    [png writeToFile:outPath atomically:YES];
}

CVPixelBufferRef pixelBufferFromImage(NSImage *image, int width, int height) {
    NSDictionary *options = @{
        (NSString *)kCVPixelBufferCGImageCompatibilityKey: @YES,
        (NSString *)kCVPixelBufferCGBitmapContextCompatibilityKey: @YES
    };
    CVPixelBufferRef pxbuffer = NULL;
    CVReturn status = CVPixelBufferCreate(kCFAllocatorDefault, width, height, kCVPixelFormatType_32ARGB, (__bridge CFDictionaryRef)options, &pxbuffer);
    if (status != kCVReturnSuccess) return NULL;
    
    CVPixelBufferLockBaseAddress(pxbuffer, 0);
    void *pxdata = CVPixelBufferGetBaseAddress(pxbuffer);
    
    CGColorSpaceRef rgbColorSpace = CGColorSpaceCreateDeviceRGB();
    CGContextRef context = CGBitmapContextCreate(pxdata, width, height, 8, 4 * width, rgbColorSpace, kCGImageAlphaPremultipliedFirst | kCGBitmapByteOrder32Big);
    
    CGImageRef cgImage = [image CGImageForProposedRect:NULL context:NULL hints:NULL];
    CGContextDrawImage(context, CGRectMake(0, 0, width, height), cgImage);
    
    CGColorSpaceRelease(rgbColorSpace);
    CGContextRelease(context);
    CVPixelBufferUnlockBaseAddress(pxbuffer, 0);
    
    return pxbuffer;
}

int main() {
    @autoreleasepool {
        NSString *pkg = @"/Users/rajkumar/authencation lec18 asd/Emergent_AI_Package";
        NSLog(@"Step 1: Generating Code Slides...");
        
        // Slide 1: reset_scene
        drawCodeSlide(
            @"Scene Reset & EEVEE Engine Setup",
            @"Function: reset_scene() in create_solar_system.py",
            @"def reset_scene():\n"
             "    bpy.ops.wm.read_factory_settings(use_empty=True)\n"
             "    scene = bpy.context.scene\n"
             "    scene.render.engine = 'BLENDER_EEVEE'   # Real-time lighting & bloom\n"
             "    scene.render.fps = 30                  # Smooth 30 frames per second\n"
             "    scene.frame_start = 1\n"
             "    scene.frame_end = 360                  # Complete looping timeline\n"
             "    return scene",
            @"Wipes the default startup cube/lamp, selects the high-performance EEVEE real-time engine, and sets a 360-frame loop.",
            [pkg stringByAppendingPathComponent:@"Code_Slide_01.png"]
        );
        
        // Slide 2: Starfield
        drawCodeSlide(
            @"Procedural Deep Space Starfield",
            @"Function: create_starfield_world()",
            @"def create_starfield_world():\n"
             "    world = bpy.data.worlds.new(\"CosmicWorld\")\n"
             "    voronoi = tree.nodes.new('ShaderNodeTexVoronoi')\n"
             "    voronoi.inputs['Scale'].default_value = 140.0\n"
             "    ramp = tree.nodes.new('ShaderNodeValToRGB')\n"
             "    ramp.color_ramp.elements[0].position = 0.965  # Pitch black deep space\n"
             "    ramp.color_ramp.elements[1].position = 0.985  # Brilliant pinpoint stars\n"
             "    links.new(voronoi.outputs['Distance'], ramp.inputs['Fac'])",
            @"Using mathematical Voronoi noise creates an infinite-resolution starfield that never gets blurry regardless of camera zoom.",
            [pkg stringByAppendingPathComponent:@"Code_Slide_02.png"]
        );
        
        // Slide 3: Sun Material & Point Light
        drawCodeSlide(
            @"Sun Surface Material & Physical Point Light",
            @"Function: create_sun_material() & build_solar_system()",
            @"# Fiery Plasma Noise Shader:\n"
             "noise = nodes.new('ShaderNodeTexNoise')\n"
             "noise.inputs['Scale'].default_value = 5.0\n"
             "bsdf.inputs['Emission Strength'].default_value = 14.0\n\n"
             "# Physical Point Light at Origin:\n"
             "light_data = bpy.data.lights.new(name=\"Sun_PointLight\", type='POINT')\n"
             "light_data.energy = 18000.0   # 18,000 W power casts realistic light\n"
             "light_data.shadow_soft_size = 4.0",
            @"The Sun requires both a high-emission material to glow on camera AND a high-energy Point Light to cast realistic sunlight onto all planets.",
            [pkg stringByAppendingPathComponent:@"Code_Slide_03.png"]
        );
        
        // Slide 4: Earth Surface & Clouds
        drawCodeSlide(
            @"Earth Surface, Ice Caps & 3D Cloud Sphere",
            @"Functions: create_earth_material() & create_earth_cloud_material()",
            @"# Continents vs Oceans:\n"
             "noise_land = nodes.new('ShaderNodeTexNoise')  # Coastlines and terrain\n"
             "links.new(ramp_rough.outputs['Color'], bsdf.inputs['Roughness']) # Water: 0.08, Land: 0.85\n\n"
             "# Polar Ice Caps (Absolute Z treating North and South poles symmetrically):\n"
             "math_abs.operation = 'ABSOLUTE'\n"
             "links.new(sep_xyz.outputs['Z'], math_abs.inputs[0])\n\n"
             "# Floating 3D Cloud Sphere (scale 1.018 hovering above surface):\n"
             "cloud_obj.parent = planet_obj; d_clouds.driver.expression = \"frame * 0.056\"",
            @"100% procedural with zero external image files. Generates glossy oceans, matte continents, polar ice, and independently drifting clouds.",
            [pkg stringByAppendingPathComponent:@"Code_Slide_04.png"]
        );
        
        // Slide 5: Jupiter & Saturn Rings
        drawCodeSlide(
            @"Jupiter Atmospheric Bands & Saturn's Rings",
            @"Functions: create_jupiter_material() & create_saturn_ring_material()",
            @"# Jupiter Wave Texture along Z-axis for turbulent atmospheric stripes:\n"
             "wave.wave_type = 'BANDS'; wave.bands_direction = 'Z'\n\n"
             "# Saturn Ring Radial Distance: sqrt(X^2 + Y^2)\n"
             "math_dist.operation = 'SQRT'\n\n"
             "# Cassini Division Gap in Alpha Ramp:\n"
             "cr_a.elements.new(0.60).color = (0.02, 0.02, 0.02, 1.0) # Transparent Gap!\n"
             "links.new(ramp_alpha.outputs['Color'], bsdf.inputs['Alpha'])",
            @"Uses mathematical distance from Saturn's center to carve out the transparent Cassini Division gap between the A and B rings.",
            [pkg stringByAppendingPathComponent:@"Code_Slide_05.png"]
        );
        
        // Slide 6: Animation Drivers
        drawCodeSlide(
            @"Mathematical Keplerian Animation Drivers",
            @"Implementation: driver_add('rotation_euler', 2)",
            @"# Continuous Orbital Revolutions without manual keyframes:\n"
             "pivot = bpy.data.objects.new(f\"Pivot_{p_name}\", None)\n"
             "d_orb = pivot.driver_add('rotation_euler', 2) # Z Axis\n"
             "d_orb.driver.expression = f\"frame * {orb_speed}\"\n\n"
             "# Speed scale obeying Keplerian mechanics:\n"
             "# Mercury: 0.040 | Venus: 0.026 | Earth: 0.018 | Mars: 0.013\n"
             "# Jupiter: 0.0075 | Saturn: 0.0050 | Uranus: 0.0033 | Neptune: 0.0022",
            @"Drivers calculate rotation directly from the timeline frame. The animation loops forever and automatically matches astronomical orbital speeds.",
            [pkg stringByAppendingPathComponent:@"Code_Slide_06.png"]
        );
        
        // Slide 7: Collections & Camera
        drawCodeSlide(
            @"Outliner Hierarchy & Camera Track-To Constraint",
            @"Implementation: Scene Collections & Constraints",
            @"# Clean Collection Organization in Outliner:\n"
             "col_sun = bpy.data.collections.new(\"01_Sun_and_Lighting\")\n"
             "col_planets = bpy.data.collections.new(\"02_Planets\")\n"
             "col_orbits = bpy.data.collections.new(\"03_Orbit_Paths\")\n\n"
             "# Camera Auto-Tracking Lock:\n"
             "cam_obj = bpy.data.objects.new(\"Camera\", cam_data)\n"
             "tt = cam_obj.constraints.new(type='TRACK_TO')\n"
             "tt.target = sun_obj; tt.track_axis = 'TRACK_NEGATIVE_Z'",
            @"Maintains clean modular project hierarchy and ensures the camera stays perfectly locked on the solar system center regardless of movement.",
            [pkg stringByAppendingPathComponent:@"Code_Slide_07.png"]
        );
        
        NSLog(@"Step 2: Encoding Video Stream with all 16 Scenes...");
        
        // Build timeline segments: (ImagePath, DurationSeconds)
        NSArray *segments = @[
            @[ [pkg stringByAppendingPathComponent:@"Solar_System_Overview.png"], @25 ],
            @[ [pkg stringByAppendingPathComponent:@"Sun_shot.png"], @40 ],
            @[ [pkg stringByAppendingPathComponent:@"Mercury_shot.png"], @35 ],
            @[ [pkg stringByAppendingPathComponent:@"Venus_shot.png"], @35 ],
            @[ [pkg stringByAppendingPathComponent:@"Earth_shot.png"], @40 ],
            @[ [pkg stringByAppendingPathComponent:@"Earth_Closeup.png"], @35 ],
            @[ [pkg stringByAppendingPathComponent:@"Mars_shot.png"], @35 ],
            @[ [pkg stringByAppendingPathComponent:@"Jupiter_shot.png"], @35 ],
            @[ [pkg stringByAppendingPathComponent:@"Saturn_shot.png"], @34 ],
            // Part 2 Code Slides:
            @[ [pkg stringByAppendingPathComponent:@"Code_Slide_01.png"], @51 ],
            @[ [pkg stringByAppendingPathComponent:@"Code_Slide_02.png"], @50 ],
            @[ [pkg stringByAppendingPathComponent:@"Code_Slide_03.png"], @50 ],
            @[ [pkg stringByAppendingPathComponent:@"Code_Slide_04.png"], @50 ],
            @[ [pkg stringByAppendingPathComponent:@"Code_Slide_05.png"], @50 ],
            @[ [pkg stringByAppendingPathComponent:@"Code_Slide_06.png"], @50 ],
            @[ [pkg stringByAppendingPathComponent:@"Code_Slide_07.png"], @58 ],
        ];
        
        NSString *rawVideoPath = [pkg stringByAppendingPathComponent:@"temp_raw_video.mp4"];
        [[NSFileManager defaultManager] removeItemAtPath:rawVideoPath error:nil];
        
        NSError *writerError = nil;
        AVAssetWriter *writer = [[AVAssetWriter alloc] initWithURL:[NSURL fileURLWithPath:rawVideoPath] fileType:AVFileTypeMPEG4 error:&writerError];
        NSDictionary *vSettings = @{
            AVVideoCodecKey: AVVideoCodecTypeH264,
            AVVideoWidthKey: @1920,
            AVVideoHeightKey: @1080
        };
        AVAssetWriterInput *vInput = [AVAssetWriterInput assetWriterInputWithMediaType:AVMediaTypeVideo outputSettings:vSettings];
        vInput.expectsMediaDataInRealTime = NO;
        AVAssetWriterInputPixelBufferAdaptor *adaptor = [AVAssetWriterInputPixelBufferAdaptor assetWriterInputPixelBufferAdaptorWithAssetWriterInput:vInput sourcePixelBufferAttributes:nil];
        
        [writer addInput:vInput];
        [writer startWriting];
        [writer startSessionAtSourceTime:kCMTimeZero];
        
        int currentSec = 0;
        for (NSArray *seg in segments) {
            NSString *imgPath = seg[0];
            int duration = [seg[1] intValue];
            NSImage *img = [[NSImage alloc] initWithContentsOfFile:imgPath];
            if (!img) {
                NSLog(@"Warning: Image not found: %@", imgPath);
                continue;
            }
            CVPixelBufferRef pBuf = pixelBufferFromImage(img, 1920, 1080);
            for (int s = 0; s < duration; s++) {
                while (!vInput.isReadyForMoreMediaData) {
                    [NSThread sleepForTimeInterval:0.005];
                }
                CMTime time = CMTimeMake(currentSec + s, 1);
                [adaptor appendPixelBuffer:pBuf withPresentationTime:time];
            }
            CVPixelBufferRelease(pBuf);
            currentSec += duration;
        }
        
        [vInput markAsFinished];
        dispatch_semaphore_t sema1 = dispatch_semaphore_create(0);
        [writer finishWritingWithCompletionHandler:^{
            dispatch_semaphore_signal(sema1);
        }];
        dispatch_semaphore_wait(sema1, DISPATCH_TIME_FOREVER);
        NSLog(@"Video encoded successfully: %d total seconds", currentSec);
        
        NSLog(@"Step 3: Muxing with 11-Minute Male Audio Track...");
        NSString *audioPath = [pkg stringByAppendingPathComponent:@"Full_10Min_Solar_System_Presentation_MaleVoice.m4a"];
        NSString *finalVideoPath = [pkg stringByAppendingPathComponent:@"Solar_System_10Min_Presentation.mp4"];
        [[NSFileManager defaultManager] removeItemAtPath:finalVideoPath error:nil];
        
        AVURLAsset *vAsset = [AVURLAsset URLAssetWithURL:[NSURL fileURLWithPath:rawVideoPath] options:nil];
        AVURLAsset *aAsset = [AVURLAsset URLAssetWithURL:[NSURL fileURLWithPath:audioPath] options:nil];
        
        AVMutableComposition *comp = [AVMutableComposition composition];
        AVMutableCompositionTrack *cVideo = [comp addMutableTrackWithMediaType:AVMediaTypeVideo preferredTrackID:kCMPersistentTrackID_Invalid];
        AVMutableCompositionTrack *cAudio = [comp addMutableTrackWithMediaType:AVMediaTypeAudio preferredTrackID:kCMPersistentTrackID_Invalid];
        
        CMTime duration = aAsset.duration;
        [cVideo insertTimeRange:CMTimeRangeMake(kCMTimeZero, duration) ofTrack:[[vAsset tracksWithMediaType:AVMediaTypeVideo] firstObject] atTime:kCMTimeZero error:nil];
        [cAudio insertTimeRange:CMTimeRangeMake(kCMTimeZero, duration) ofTrack:[[aAsset tracksWithMediaType:AVMediaTypeAudio] firstObject] atTime:kCMTimeZero error:nil];
        
        AVAssetExportSession *exporter = [[AVAssetExportSession alloc] initWithAsset:comp presetName:AVAssetExportPresetHighestQuality];
        exporter.outputURL = [NSURL fileURLWithPath:finalVideoPath];
        exporter.outputFileType = AVFileTypeMPEG4;
        
        dispatch_semaphore_t sema2 = dispatch_semaphore_create(0);
        [exporter exportAsynchronouslyWithCompletionHandler:^{
            NSLog(@"Export Status: %ld, error: %@", (long)exporter.status, exporter.error);
            dispatch_semaphore_signal(sema2);
        }];
        dispatch_semaphore_wait(sema2, DISPATCH_TIME_FOREVER);
        
        [[NSFileManager defaultManager] removeItemAtPath:rawVideoPath error:nil];
        NSLog(@"COMPLETE! Final presentation video generated at %@", finalVideoPath);
    }
    return 0;
}
