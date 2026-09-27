// Increase $fn for smoother corners (optional)
$fn = 64;


width = 130.0;
length = 175.0;
thickness = 8.0;

screw_w = 117.0;
screw_l = 160.0;

screw_dia = 4.5;

case_corner_radius = 6.0;


// Module: create a 2D rounded‐rectangle of width=w, height=h and corner‐radius=r
module roundedRect2D(w, h, r) {
    // The inner square is (w−2r)×(h−2r).  Minkowski with a circle of radius=r adds
    // the rounded corners (and expands back to w×h overall).
    translate([r, r, 0]) {
        minkowski() {
            square([w - 2*r, h - 2*r], center = false);
            circle(r = r);
        }
    }
}

module right_triangle_45_45_90_x(leg=2, length=200, center=false) {
    rotate([0, 90, 0])
        linear_extrude(height=length, center=center)
            polygon(points=[
                [0,0],
                [leg,leg],
                [0,leg]
            ]);
}

module right_triangle_45_45_90_y(leg=2, length=200, center=false) {
    rotate([-90, 0, 0])
        linear_extrude(height=length, center=center)
            polygon(points=[
                [0,0],
                [leg,leg],
                [0,leg]
            ]);
}

module right_triangle_45_45_90_z(leg=2, length=200, center=false) {
    linear_extrude(height=length, center=center)
        polygon(points=[
            [0,0],
            [leg,leg],
            [0,leg]
        ]);
}

module right_triangle_45_45_90_x_mirror(leg=2, length=200, center=false) {
    mirror([0,1,0])
        right_triangle_45_45_90_x(leg=leg, length=length, center=center);
}

module right_triangle_45_45_90_y_mirror(leg=2, length=200, center=false) {
    mirror([1,0,0])
        right_triangle_45_45_90_y(leg=leg, length=length, center=center);
}

module right_triangle_45_45_90_z_mirror(leg=2, length=200, center=false) {
    mirror([0,0,1])
        right_triangle_45_45_90_z(leg=leg, length=length, center=center);
}


module mkScrewMountTriangle(mode="positive", length=8) {
    insert_dia = 3.9;    
    
    if (mode == "positive") {
        color("orange") 
        difference() {
            union() {
                right_triangle_45_45_90_y(leg=6, length=length, center=false);    
                translate([0, 0, -8.5]) cube([6, length, 2.5]);  // Add some to top
            }   
            translate([6/2, length/2, -8-0.5-0.1]) cylinder(h=7+1, d=insert_dia);
        }
    } else if (mode == "negative") {
        // Redo the insert cut
        translate([6/2, length/2, -8-0.5-0.1]) cylinder(h=7+1, d=insert_dia);
    }
        
}


module mkScrewMountCover(mode="positive", length=8) {
    screw_dia = 3;    
    
    if (mode == "positive") {
        // Currently unused
        /*
        color("orange") 
        difference() {
            union() {
                right_triangle_45_45_90_y(leg=6, length=length, center=false);    
                translate([0, 0, -8.5]) cube([6, length, 2.5]);  // Add some to top
            }   
            translate([6/2, length/2, -8-0.5-0.1]) cylinder(h=7+1, d=insert_dia);
        }
        */
        
    } else if (mode == "negative") {
        // Redo the insert cut
        translate([6/2, length/2, -8-0.5-0.1]) cylinder(h=7+1, d=screw_dia);
    }
        
}



module mkCableChannel() {
    difference() {
        cube([5, 10, 4]);
        translate([2.51, 2.5, -1]) color("blue") cube([2.5, 5, 6]);
    }
    
    /*
    inner_height = 5.0;
    thickness = 9.0;
    depth = 6.0;
    
    difference() {
        cube([depth, thickness, inner_height+6]);
        hull() {
            translate([0, thickness+1, (inner_height+6)/2]) rotate([90, 0, 0]) cylinder(d=inner_height, h=thickness+2);
            translate([depth-2, thickness+1, (inner_height+6)/2]) rotate([90, 0, 0]) cylinder(d=inner_height, h=thickness+2);
        }
    }   
    
    translate([1, (thickness-4)/2, -1]) color("blue") cube([2, 4, inner_height+6+2]);
    */
}

module mkBackCrossbrace() {
    side_size = 2.0;
    lengthc = 14.0;
    widthc = width - (2*side_size) - 0.25;
    
    difference() {
    union() {
    translate([side_size, 0, 0]) {         
        difference() {        
        union() {
        rotate([-45, 0, 0]) {
            difference() {
                // Main piece
                color("blue") cube([widthc, lengthc, 3]);
                // Screw holes
                translate([3, (lengthc/2)-1, -1]) color("red") cylinder(d=3, h=3+2);
                translate([widthc-3, (lengthc/2)-1, -1]) color("red") cylinder(d=3, h=3+2);
                               
            }            
        }
        
        // Main piece with 2 bolt holes
        translate([6.25, -0, 3]) { 
            right_triangle_45_45_90_x(leg=12, length=widthc-(6.25*2));
            cube([widthc-(6.25*2), 12, 2]);
        }
        }
        
        
        // Top (cut off)
        translate([0, 10, -10]) {
            cube([widthc, 3, 3]);
        }
        }
        
        // Bottom
        cube([widthc, 3, 3]);
        
    }
    
    // Holder (bottom)
    brass_insert_dia = 3.9;
      
    translate([(widthc/2)-7.5, -7, 3]) {
        difference() {
            cube([10, 10, 4]);
            translate([5, 3, -1]) color("red") cylinder(d=brass_insert_dia, h=4+2);
        }
    }
    

    // Rim (bottom)
    translate([side_size+10, -2, 3]) {
            cube([widthc-20, 5, 2]);                    
    }


    // Holder (bottom)    
    translate([(widthc/2)-7.5, 7, -10+3]) {
        difference() {
            cube([10, 12, 4]);
            translate([5, 10-2, -1]) color("red") cylinder(d=brass_insert_dia, h=4+2);
        }
    }

    // Rim (top)
    translate([side_size+10, 8, -10+3]) {
            cube([widthc-20, 5, 2]);                    
    }
    }
    
    // Cut off a small part on the bottom of the sides at a 45 degree angle
    // One side
    translate([side_size-0.1, 0, 4.24]) {
        color("purple") rotate([-45, 0, 0]) cube([6.35, 5, 5]);        
    }
    // Other side
    translate([widthc-8+3.75, 0, 4.24]) {
        color("purple") rotate([-45, 0, 0]) cube([6.5, 5, 5]);        
    }
    
    // Center cutout    
    translate([(widthc/2)+2.5, -7, 3]) color("purple") cube([15, 30, 4]);

    }

    
    
}

module mkBackCover1() {
    side_size = 2.0;
    lengthc = 14.0;
    widthc = width - (2*side_size) - 0.25;
    
    //roundedRect2D(width-(2*side_size), length-(2*side_size), r=case_corner_radius);  // 5mm corner radius
    
    difference() {
    union() {
    translate([side_size, 0, 0]) {         
        difference() {        
        union() {
        rotate([-45, 0, 0]) {
            difference() {
                // Main piece
                color("blue") cube([widthc, lengthc, 3]);
                // Screw holes
                //translate([3, (lengthc/2)-1, -1]) color("red") cylinder(d=3, h=3+2);
                //translate([widthc-3, (lengthc/2)-1, -1]) color("red") cylinder(d=3, h=3+2);
                               
            }            
        }
        
        // Main piece with 2 bolt holes
        translate([6.25, -0, 3]) right_triangle_45_45_90_x(leg=12, length=widthc-(6.25*2));                    
        }
        
        }
        
        // Bottom
        cube([widthc, 3, 3]);
        
        // Top plate
        translate([0, 10, -10]) {  
            color("purple")  union() {
            linear_extrude(height = 3) {
                roundedRect2D(widthc, (length/2)-10-side_size-0.25, r=case_corner_radius);  // 5mm corner radius
            }
            cube([widthc, 10, 3]);
            }
        }
        
        // Bottomplate
        color("purple") union() {
        translate([0, -(length/2)+side_size+0.25, -0]) {                        
             linear_extrude(height = 3) {
                roundedRect2D(widthc, (length/2)-side_size-0.25, r=case_corner_radius);  // 5mm corner radius
            }            
        }
        translate([0, -10, -0]) cube([widthc, 10, 3]);
        }
        
        
        // Circles: Sensor Apertures
        translate([-side_size, -length/2, 18-3.5-0.5]) {        
            // Thermal camera
            translate([width-2-19, 100+5+4, -25]) cylinder(d=15+4, h=6+3.5);
            // Visible camera
            translate([width-2-19, 100+5+4+24, -25]) cylinder(d=10+4, h=3+3.5-1);      // Camera
            translate([width-2-19, 100+5+4+24+10, -25]) cylinder(d=3+4, h=1+3.5);    // Microphone 1
            translate([width-2-19, 100+5+4+24-10, -25]) cylinder(d=3+4, h=1+3.5);    // Microphone 2
            translate([width-2-19+10, 100+5+4+24, -25]) cylinder(d=3+4, h=1+3.5);    // Microphone 1
            translate([width-2-19-10, 100+5+4+24, -25]) cylinder(d=3+4, h=1+3.5);    // Microphone 2
            
            // Spectrometer
            translate([width-2-19, 100+5+4+24+27, -25]) cylinder(d=5+6, h=6+3.5-3);
        }    

        
        // Circle: Sparkfun Breakout (bottom)
        translate([-side_size, -22-28, 0.0]) {
            // Cut
            translate([0, (length/2)-side_size-4, -11]) {
                translate([width/2, 0, 0]) cylinder(d=12+4, h=5);        
            }
        }
        // Circle: Sparkfun Breakout (top)
        translate([-side_size, -22, 0.0]) {
            // Cut
            translate([0, (length/2)-side_size-4, -11]) {
                translate([width/2, 0, 0]) cylinder(d=12+4, h=5);        
            }
        }
        
        // Artistic circles
        translate([-side_size-85, -length/2, 18-3.5]) {        
            // Thermal camera
            translate([width-2-19, 100+5+4, -25]) cylinder(d=6+6, h=1);
            // Visible camera
            translate([width-2-19, 100+5+4+24, -25]) cylinder(d=2+4, h=1);      // Camera
            //translate([width-2-19, 100+5+4+24+10, -25]) cylinder(d=3+4, h=1);    // Microphone 1
            //translate([width-2-19, 100+5+4+24-10, -25]) cylinder(d=3+4, h=1);    // Microphone 2
            translate([width-2-19+10, 100+5+4+24, -25]) cylinder(d=3+4, h=1);    // Microphone 1
            translate([width-2-19-10, 100+5+4+24, -25]) cylinder(d=3+4, h=1);    // Microphone 2
            
            // Spectrometer
            translate([width-2-19, 100+5+4+24+27, -25]) cylinder(d=5+6, h=1);
            
            // Lines
            translate([width-2-19, 100+5+4+25, -25+0.5]) cube([2, 50, 1], center=true);
            translate([width-2-19, 100+5+4+25-1, -25+0.5]) rotate([0, 0, 90]) cube([2, 20, 1], center=true);
            translate([width-2-19+85, 100+5+4+25, -25+0.5]) cube([2, 50, 1], center=true);
            
            translate([width-2-19+85-30+5, 100+5+4+25-5, -25+0.5]) rotate([0, 0, 48]) cube([2, 50, 1], center=true);
            translate([width-2-19+85-30+5, 100+5+4+25+4, -25+0.5]) rotate([0, 0, -48]) cube([2, 60, 1], center=true);
            
            translate([width-2-19+85-30+5-40, 100+5+4+25-5-15, -25+0.5]) rotate([0, 0, 106]) cube([2, 50, 1], center=true);
            translate([width-2-19+85-30+5-40+5, 100+5+4+25-5-3, -25+0.5]) rotate([0, 0, -115]) cube([2, 30, 1], center=true);
            
            translate([width-2-19+85-30+5-40, 100+5+4+25-5-15+40, -25+0.5]) rotate([0, 0, -106]) cube([2, 50, 1], center=true);
            translate([width-2-19+85-30+5-40+5, 100+5+4+25-5-3+14, -25+0.5]) rotate([0, 0, 115]) cube([2, 30, 1], center=true);
            
            translate([width-2-19-5, 100+5+4+10, -25+0.5]) rotate([0, 0, 20]) cube([2, 30, 1], center=true);
            translate([width-2-19-5, 100+5+4+40, -25+0.5]) rotate([0, 0, -20]) cube([2, 30, 1], center=true);
        }    
        
        
        
        
    }
    
    }
    
    // Cut off a small part on the bottom of the sides at a 45 degree angle
    // One side
    translate([side_size-0.1, 0, 4.24]) {
        color("purple") rotate([-45, 0, 0]) cube([6.35, 5, 5]);        
    }
    // Other side
    translate([widthc-8+3.75, 0, 4.24]) {
        color("purple") rotate([-45, 0, 0]) cube([6.5, 5, 5]);        
    }
    
    // Center cutout    
    //translate([(widthc/2)+2.5, -7, 3]) color("purple") cube([15, 30, 4]);    

    // Offset
    translate([0, -length/2, 10]) {
        // cuts for the screw holders (bottom section)
        translate([2, 15, -12+8.5]) mkScrewMountCover(mode="negative");
        translate([2, 75, -12+8.5]) mkScrewMountCover(mode="negative");
        
        translate([width-2, 75, -12+8.5]) mirror([1, 0, 0]) mkScrewMountCover(mode="negative");
        translate([width-2, 15, -12+8.5]) mirror([1, 0, 0]) mkScrewMountCover(mode="negative");
        
        translate([23, 2, -12+8.5]) rotate([0, 0, 90]) mkScrewMountCover(mode="negative");
        translate([width-17, 2, -12+8.5]) rotate([0, 0, 90]) mkScrewMountCover(mode="negative");
        
        // screw holders (top section)   
        translate([2, 100, -25+11.5]) mkScrewMountCover(mode="negative");
        translate([2, 155, -25+11.5]) mkScrewMountCover(mode="negative");

        translate([width-2, 100, -25+11.5]) mirror([1, 0, 0]) mkScrewMountCover(mode="negative");
        translate([width-2, 155, -25+11.5]) mirror([1, 0, 0]) mkScrewMountCover(mode="negative");
        
        translate([37, length-2, -25+11.5]) rotate([0, 0, 270]) mkScrewMountCover(mode="negative");
        translate([width-43, length-2, -25+11.5]) rotate([0, 0, 270]) mkScrewMountCover(mode="negative");
    }
        
    // Sensor Apertures
    translate([0, -length/2, 15-1]) {        
        // Thermal camera
        translate([width-2-19, 100+5+4, -25]) cylinder(d=15, h=10+2);
        // Visible camera
        translate([width-2-19, 100+5+4+24, -25]) cylinder(d=10, h=10+2);      // Camera
        translate([width-2-19, 100+5+4+24+10, -25]) cylinder(d=3, h=10+2);    // Microphone 1
        translate([width-2-19, 100+5+4+24-10, -25]) cylinder(d=3, h=10+2);    // Microphone 2
        translate([width-2-19+10, 100+5+4+24, -25]) cylinder(d=3, h=10+2);    // Microphone 1
        translate([width-2-19-10, 100+5+4+24, -25]) cylinder(d=3, h=10+2);    // Microphone 2
        
        // Spectrometer
        translate([width-2-19, 100+5+4+24+27, -25]) cylinder(d=5, h=10+2);
    }    
 
    translate([0, -22, 0]) {
        // Cut
        translate([0, (length/2)-side_size-4, -11]) {
            translate([width/2, 0, 0]) cylinder(d=12, h=10);        
        }
    }

    translate([0, -22-28, 0]) {
        // Cut
        translate([0, (length/2)-side_size-4, -11]) {
            translate([width/2, 0, 0]) cylinder(d=12, h=10);        
        }
    }
    
    
    }
 
    // More sensor apertures (Sparkfun breakouts)
    translate([0, -22, 0]) {
    // Cut
    /*
    translate([0, (length/2)-side_size-4, -11]) {
        translate([width/2, 0, 0]) cylinder(d=10, h=10);        
    }
    */
    
    // Add
    translate([0, (length/2)-side_size-4, -11+4]) {
        translate([width/2 + 10, 10, 0]) difference() { cylinder(d=7, h=4); cylinder(d=4, h=5); }
        translate([width/2 - 10, 10, 0]) difference() { cylinder(d=7, h=4); cylinder(d=4, h=5); }
        translate([width/2 - 10, - 10, 0]) difference() { cylinder(d=7, h=4); cylinder(d=4, h=5); }
        translate([width/2 + 10, - 10, 0]) difference() { cylinder(d=7, h=4); cylinder(d=4, h=5); }
    }

    }

    // More sensor apertures (Sparkfun breakouts)
    translate([0, -22-28, 0]) {
    /*
    // Cut
    translate([0, (length/2)-side_size-4, -11]) {
        translate([width/2, 0, 0]) cylinder(d=10, h=10);        
    }
    */
    
    // Add
    translate([0, (length/2)-side_size-4, -11+4]) {
        translate([width/2 + 10, 10, 0]) difference() { cylinder(d=7, h=4); cylinder(d=4, h=5); }
        translate([width/2 - 10, 10, 0]) difference() { cylinder(d=7, h=4); cylinder(d=4, h=5); }
        translate([width/2 - 10, - 10, 0]) difference() { cylinder(d=7, h=4); cylinder(d=4, h=5); }
        translate([width/2 + 10, - 10, 0]) difference() { cylinder(d=7, h=4); cylinder(d=4, h=5); }
    }

    // QWIIC hub
    translate([-35, (length/2)-side_size-4-10, -11+4]) {
        translate([width/2 + 5, 10, 0]) difference() { cylinder(d=7, h=4); cylinder(d=4, h=5); }
        translate([width/2 - 5, 10, 0]) difference() { cylinder(d=7, h=4); cylinder(d=4, h=5); }
    }


    }
    
    
}



module mkBack() {
    height_above = 25.0;
    difference() {            
        // Extrude the 2D rounded rectangle to 5 mm height
        translate([0, 0, -height_above]) {
            difference() {
                linear_extrude(height = thickness+height_above) {
                    roundedRect2D(width, length, r=case_corner_radius);  // 5mm corner radius
                }
    
                // Now hollow out the interior
                side_size = 2.0;
                translate([side_size, side_size, -0.1]) linear_extrude(height = height_above+0.1) {
                    roundedRect2D(width-(2*side_size), length-(2*side_size), r=case_corner_radius);  // 5mm corner radius
                }
            }
            
/*            
         // Small stablizer from bottom to overhang
        translate([39, length/2, -25+height_above]) cube([3, 3, 25]);
        translate([width-34, length/2, -25+height_above]) cube([3, 3, 25]);

        difference() {
            translate([width, length/2+3, 10]) rotate([180, 0, 270]) color("blue") slanting_cube(5, 5+10, width, 10);
            translate([width+1, (length/2), 10]) rotate([180, 0, 270]) color("red") slanting_cube(5, 5+10, width+10, 10.1);        
        }
        translate([0, length/2, 10]) color("blue") cube([width, 3, 2]);
*/
        }        
 
        
        // Add the screws
        screw_offset_x = (width-screw_w)/2;
        screy_offset_y = (length-screw_l)/2;
        translate([screw_offset_x, screy_offset_y, -1]) color("blue") cylinder(h=thickness+2, d=screw_dia); 
        translate([screw_offset_x, screy_offset_y, -1]) color("blue") cylinder(h=4.5, d=9); 
        translate([screw_offset_x+screw_w, screy_offset_y, -1]) color("blue") cylinder(h=thickness+2, d=screw_dia); 
        translate([screw_offset_x+screw_w, screy_offset_y, -1]) color("blue") cylinder(h=4.5, d=9); 
        translate([screw_offset_x, screy_offset_y+screw_l, -1]) color("blue") cylinder(h=thickness+2, d=screw_dia); 
        translate([screw_offset_x, screy_offset_y+screw_l, -1]) color("blue") cylinder(h=4.5, d=9); 
        translate([screw_offset_x+screw_w, screy_offset_y+screw_l, -1]) color("blue") cylinder(h=thickness+2, d=screw_dia); 
        translate([screw_offset_x+screw_w, screy_offset_y+screw_l, -1]) color("blue") cylinder(h=4.5, d=9); 
    
        // Slightly wonky size, but cutout should be OK    
        translate([width+1, length/2, -height_above+10-0.1]) rotate([180, 0, 270]) color("red") slanting_cube(width, width+10, length, 10);

    }
    
    
    // Triangle lip around perimeter
    difference() {
        union() {
            translate([2, 15, -12+3]) right_triangle_45_45_90_y(leg=3, length=75, center=false);
            translate([width-2, 15, -12+3]) right_triangle_45_45_90_y_mirror(leg=3, length=75, center=false);
            translate([2, (length/2)+10+1.1, -25+3+3]) right_triangle_45_45_90_y(leg=3, length=60, center=false);
            translate([width-2, (length/2)+10+1.1, -25+3+3]) right_triangle_45_45_90_y_mirror(leg=3, length=60, center=false);
        
            translate([15, 3+2, -12]) rotate([180, 0, 0])right_triangle_45_45_90_x(leg=3, length=width-15-15-2, center=false);
            
            translate([15, length-5, -25+3]) rotate([180, 0, 0])right_triangle_45_45_90_x_mirror(leg=3, length=60, center=false);
            translate([15+75, length-5, -25+3]) rotate([180, 0, 0])right_triangle_45_45_90_x_mirror(leg=3, length=15, center=false);
        
            // screw holders (bottom section)   
            translate([2, 15, -12+8.5]) mkScrewMountTriangle(mode="positive");
            translate([2, 75, -12+8.5]) mkScrewMountTriangle(mode="positive");
            
            translate([width-2, 75, -12+8.5]) mirror([1, 0, 0]) mkScrewMountTriangle(mode="positive");
            translate([width-2, 15, -12+8.5]) mirror([1, 0, 0]) mkScrewMountTriangle(mode="positive");
            
            translate([23, 2, -12+8.5]) rotate([0, 0, 90]) mkScrewMountTriangle(mode="positive");
            translate([width-17, 2, -12+8.5]) rotate([0, 0, 90]) mkScrewMountTriangle(mode="positive");
            
            // screw holders (top section)   
            translate([2, 100, -25+11.5]) mkScrewMountTriangle(mode="positive");
            translate([2, 155, -25+11.5]) mkScrewMountTriangle(mode="positive");

            translate([width-2, 100, -25+11.5]) mirror([1, 0, 0]) mkScrewMountTriangle(mode="positive");
            translate([width-2, 155, -25+11.5]) mirror([1, 0, 0]) mkScrewMountTriangle(mode="positive");
            
            translate([37, length-2, -25+11.5]) rotate([0, 0, 270]) mkScrewMountTriangle(mode="positive");
            translate([width-43, length-2, -25+11.5]) rotate([0, 0, 270]) mkScrewMountTriangle(mode="positive");
            
        }
        
        // cuts for the screw holders (bottom section)
        translate([2, 15, -12+8.5]) mkScrewMountTriangle(mode="negative");
        translate([2, 75, -12+8.5]) mkScrewMountTriangle(mode="negative");
        
        translate([width-2, 75, -12+8.5]) mirror([1, 0, 0]) mkScrewMountTriangle(mode="negative");
        translate([width-2, 15, -12+8.5]) mirror([1, 0, 0]) mkScrewMountTriangle(mode="negative");
        
        translate([23, 2, -12+8.5]) rotate([0, 0, 90]) mkScrewMountTriangle(mode="negative");
        translate([width-17, 2, -12+8.5]) rotate([0, 0, 90]) mkScrewMountTriangle(mode="negative");
        
        // screw holders (top section)   
        translate([2, 100, -25+11.5]) mkScrewMountTriangle(mode="negative");
        translate([2, 155, -25+11.5]) mkScrewMountTriangle(mode="negative");

        translate([width-2, 100, -25+11.5]) mirror([1, 0, 0]) mkScrewMountTriangle(mode="negative");
        translate([width-2, 155, -25+11.5]) mirror([1, 0, 0]) mkScrewMountTriangle(mode="negative");
        
        translate([37, length-2, -25+11.5]) rotate([0, 0, 270]) mkScrewMountTriangle(mode="negative");
        translate([width-43, length-2, -25+11.5]) rotate([0, 0, 270]) mkScrewMountTriangle(mode="negative");
        
    }
    
    // 45 degree screw mount on triangle
    // Left side
    translate([width-2, length/2+15+0.1+2, -25+10+1-2]) {
        //color("blue") cube([10, 10, 10]);
        rotate([45, 0, 180]) {
            //translate([0, 0, -11.5]) cube([2, 2, 3]);   // Depth gauge
            mkScrewMountTriangle(mode="positive", length=14.5);
        }
    }
    
    // Right side
    translate([2, length/2+15+0.1+2, -25+10+1-2]) {
        //color("blue") cube([10, 10, 10]);
        rotate([-45, 0, 0]) {
            translate([0, -14.5, 0]) {
            //translate([0, 12, -11.5]) cube([2, 2, 3]);   // Depth gauge
            mkScrewMountTriangle(mode="positive", length=14.5);
            }
        }
    }
    
    
    // Cable channels
    translate([6.9, 43, -8]) rotate([0, 0, 180]) mkCableChannel();
    translate([width-6.9, 30, -8]) mkCableChannel();
    translate([width-6.9, 65, -8]) mkCableChannel();

    // DEBUG: Crossbrace placement
    //translate([0, length/2, -15.15]) mkBackCrossbrace();
    //translate([0, length/2, -25.15]) mkBackCover1();

}



module mkPomelloMountPattern() {
    holeDia = 5.0;
    holeDepth = 6.0;
    
    offset_x = 0;
    offset_y = 0;
    
    translate([offset_x, offset_y, 0]) color("purple") cylinder(h=holeDepth, d=holeDia);
    //translate([offset_x+27, offset_y, 0]) color("purple") cylinder(h=holeDepth, d=holeDia);   // temporarily disabled
    translate([offset_x, offset_y+73, 0]) color("purple") cylinder(h=holeDepth, d=holeDia);
    translate([offset_x+27, offset_y+46, 0]) color("purple") cylinder(h=holeDepth, d=holeDia);
    
    translate([offset_x+27, offset_y+46+61, 0]) color("purple") cylinder(h=holeDepth, d=holeDia);  // Hole on the front
    
    // A rough estimate for the front
    //translate([offset_x-4, offset_y+111, -27]) color("purple") cube([35, 1, 27]);
    
    translate([offset_x+4.5, offset_y, 0]) color("purple") cube([18, 90, 2+1]);
    translate([offset_x-3, offset_y+5, 0]) color("purple") cube([18+15, 37, 2+1]);
    translate([offset_x-3, offset_y+40, 0]) color("red") cube([18, 29, 2+1]);
    translate([offset_x-3+8+7, offset_y+50, 0]) color("red") cube([18, 40, 2+1]);
    translate([offset_x-3, offset_y+77, 0]) color("red") cube([18, 13, 2+1]);            
}

module mkZero4UMountPattern() {
    holeDia = 4.0;
    holeDepth = 6.0;
    
    offset_x = 0;
    offset_y = 0;
    
    translate([offset_x, offset_y, 0]) color("purple") cylinder(h=holeDepth, d=holeDia);
    translate([offset_x+58, offset_y, 0]) color("purple") cylinder(h=holeDepth, d=holeDia);
    translate([offset_x, offset_y+23, 0]) color("purple") cylinder(h=holeDepth, d=holeDia);
    translate([offset_x+58, offset_y+23, 0]) color("purple") cylinder(h=holeDepth, d=holeDia);
        
}


module mkWaveshareThermalMountPattern() {
    // Whole unit is 62mm long x 13 wide -- excess on bottom is for the USB port.
    disty = 50.0;
    distx = 9.0;
    holeSize = 3.4;
    holeDepth = 6.0;
    
    offset_x = 0;
    offset_y = 0;
    translate([offset_x, offset_y, 0]) color("purple") cylinder(h=holeDepth, d=holeSize);
    translate([offset_x+distx, offset_y, 0]) color("purple") cylinder(h=holeDepth, d=holeSize);
    translate([offset_x, offset_y+disty, 0]) color("purple") cylinder(h=holeDepth, d=holeSize);
    translate([offset_x+distx, offset_y+disty, 0]) color("purple") cylinder(h=holeDepth, d=holeSize);        
}

module mkSpecMountPattern(mode) {
    distx = 18.0;    
    holeSize=3.8;
    holeDepth=7.0;
    offset_x = 0;
    offset_y = 0;
    
    if (mode == "positive") {
        difference() {
            translate([-3.5, -3.5, -3.5+2]) color("purple") cube([25, 7, 3.5]);        // Main block
            translate([-3.5+6.5, -3.5-0.1, -3.5-0.1]) color("green") cube([12, 7+0.2, 3.5+0.2]);     // Middle cutout
        }
        
        //translate([-3.5+6.5, -3.5-7-0.1, -3.5+6]) color("green") cube([120, 15+0.2, 3.5+0.2]);     // Middle cutout
        
    } else {
        translate([offset_x, offset_y, 2]) color("purple") cylinder(h=holeDepth, d=holeSize);
        translate([offset_x+distx, offset_y, 2]) color("purple") cylinder(h=holeDepth, d=holeSize);        
        
        //translate([-3.5+6.5, -3.5-7-0.1, -3.5+6]) color("green") cube([12, 15+0.2, 3.5+0.2]);     // Middle cutout
        
        
    }
       
}

module mkCameraMountPattern(mode) {
    distx = 21.0;    
    holeSize=3.4;
    holeDepth=7.0;
    offset_x = 0;
    offset_y = 0;
    
    if (mode == "positive") {        
        difference() {
            translate([-3.5, -3, -3.5]) color("purple") cube([28, 6, 3.5]);        // Main block
            translate([-3.5+6, -3-0.1, -3.5-0.1]) color("green") cube([16, 6+0.2, 3.5+0.2]);     // Middle cutout
        }       
                
    } else {
        translate([offset_x, offset_y, 0]) color("purple") cylinder(h=holeDepth, d=holeSize);
        translate([offset_x+distx, offset_y, 0]) color("purple") cylinder(h=holeDepth, d=holeSize);        
        
        // Also cut a hole for the cable?
        translate([-3.5, -3-18, 0]) color("green") cube([28, 3+0.2, 8]);     // Middle cutout        
    }
       
}


module mkAirParticleSensorMountPattern(mode) {
    sizex = 41.0;
    sizey = 41.0;
    sizez = 12.5;
    
    offset_x = 0;
    offset_y = 0;
    
    if (mode == "positive") {        
        //translate([0, 0, -sizez]) color("green") cube([sizex, sizey, sizez]);                
        translate([0, 0, -2.5]) color("green") {
            difference () {
                cube([sizex+3, 10, 4]);
                translate([1.5, 1.5, 0]) cube([sizex, sizey, sizez]);                
            }
        }        
    } else {
        // none
    }
       
}


module mkUSBHubMountPattern(mode="positive") {
    // Whole unit is 62mm long x 13 wide -- excess on bottom is for the USB port.
    disty = 25.5;
    distx = 15.0;
    holeSize = 3.5;
    holeDepth = 6.0;
    standoffDia = holeSize + 3.5;
    standoffHeight = 2.0;
    
    offset_x = 0;
    offset_y = 0;
    if (mode == "negative") {
        translate([offset_x, offset_y, -standoffHeight-0.1]) color("purple") cylinder(h=holeDepth+standoffHeight, d=holeSize);
        translate([offset_x+distx, offset_y, -standoffHeight-0.1]) color("purple") cylinder(h=holeDepth+standoffHeight, d=holeSize);
        translate([offset_x, offset_y+disty, -standoffHeight-0.1]) color("purple") cylinder(h=holeDepth+standoffHeight, d=holeSize);
        translate([offset_x+distx, offset_y+disty, -standoffHeight-0.1]) color("purple") cylinder(h=holeDepth+standoffHeight, d=holeSize);        
    } else {
        translate([offset_x, offset_y, -standoffHeight]) color("purple") cylinder(h=holeDepth+standoffHeight, d=standoffDia);
        translate([offset_x+distx, offset_y, -standoffHeight]) color("purple") cylinder(h=holeDepth+standoffHeight, d=standoffDia);
        translate([offset_x, offset_y+disty, -standoffHeight]) color("purple") cylinder(h=holeDepth+standoffHeight, d=standoffDia);
        translate([offset_x+distx, offset_y+disty, -standoffHeight]) color("purple") cylinder(h=holeDepth+standoffHeight, d=standoffDia);                
    }
}

module mkCM5CoolerPattern(mode="positive") {
    cm5_width = 60.0;
    cm5_length = 45.0;
    
    holeHeight = 15.0;
    
    holeBorder = 2.0;
    borderHeight = 7.0;
    
    sideDuctLength = 12.0;
    
    if (mode=="positive") {       
        difference() {
            union() {
                // The border
                color("red") translate([-holeBorder, -holeBorder, -borderHeight]) cube([cm5_width+(2*holeBorder), cm5_length+(2*holeBorder), borderHeight]);                
                // The top
                color("red") translate([-holeBorder, -holeBorder, -borderHeight-2]) cube([cm5_width+(2*holeBorder), cm5_length+(2*holeBorder), 2]);                
                // The duct (side)
                color("green") translate([holeBorder+cm5_width, -holeBorder, -borderHeight-2]) cube([sideDuctLength+(2*holeBorder), cm5_length+(2*holeBorder), borderHeight+2]);                
            }        
            // The cutouts for the side duct
            for (y_o = [0:8:42]) {
                color("blue") translate([holeBorder+cm5_width-holeBorder-1, -holeBorder+2+y_o, -borderHeight]) cube([sideDuctLength+(2*holeBorder)+holeBorder+1+1, 5, borderHeight]);                
            }
            
            // The side duct cutout
            color("blue") translate([(cm5_width/2), (cm5_length/2), -borderHeight-5]) cylinder(d=32, h=10);
        }

     
        difference() {
            union() {
            // The top duct cutout
            color("blue") translate([(cm5_width/2), (cm5_length/2)-1.75, -borderHeight-6]) {
            
                difference() {
                    hull() {
                        cylinder(d=36, h=5);
                        translate([-17+36-51, -17-5.75, 0]) cube([29+51, 36+13, 5]);
                    }
            
                    translate([0, 0, 2]) hull() {
                        cylinder(d=32, h=5);
                        translate([-15+32, -14, 0]) cube([35, 30, 5]);
                    }
                    
                }

            }

               
            // The cutouts for the side duct
            for (y_o = [0:8:22]) {
                color("green") translate([holeBorder+cm5_width-holeBorder-1-25, -holeBorder+12+3+y_o, -borderHeight-4]) cube([sideDuctLength+(2*holeBorder)+holeBorder+1+25, 3, 3]);                
            }
            
            }
        
            // The side duct cutout
            color("blue") translate([(cm5_width/2), (cm5_length/2), -borderHeight-5]) cylinder(d=32, h=10);
            
            // ESP32 mount pattern
            color("red") translate([4, 3.5, -borderHeight-5-5]) cylinder(d=4, h=10);
            color("red") translate([4+58, 3.5, -borderHeight-5-5]) cylinder(d=4, h=10);
            color("red") translate([4+58, 3.5+37, -borderHeight-5-5]) cylinder(d=4, h=10);
        }
        
    } else {
        color("red")
        translate([0, 0, -borderHeight-1]) cube([cm5_width, cm5_length, holeHeight]);        
    }
}
    

module mkESP32MountPattern(mode="positive") {
    borderHeight = 0.0;

    if (mode == "positive") {
        // ESP32 mount pattern
        d2 = 8.0;
        rotate([0, 0, 90]) {
        color("red") translate([4, 3.5, -borderHeight-5-5]) cylinder(d=d2, h=8);
        color("red") translate([4+58, 3.5, -borderHeight-5-5]) cylinder(d=d2, h=8);
        color("red") translate([4+58, 3.5+37, -borderHeight-5-5]) cylinder(d=d2, h=8);
        color("red") translate([4, 3.5+37, -borderHeight-5-5]) cylinder(d=d2, h=8);
        }

    } else if (mode == "negative") {
    
        // ESP32 mount pattern
        rotate([0, 0, 90]) {
        color("red") translate([4, 3.5, -borderHeight-5-5-1]) cylinder(d=4, h=10);
        color("red") translate([4+58, 3.5, -borderHeight-5-5-1]) cylinder(d=4, h=10);
        color("red") translate([4+58, 3.5+37, -borderHeight-5-5-1]) cylinder(d=4, h=10);
        color("red") translate([4, 3.5+37, -borderHeight-5-5-1]) cylinder(d=4, h=10);
        }
    } else if (mode == "precut") {
        // Cut a big square
        color("red") translate([-44.5, 0, -borderHeight-5-5+2-0.1]) cube([37+8, 58+8, 2.1]);
    }

}   


module mkSparkfunGenericQWIICBoardMountPattern(mode="positive") {
    borderHeight = 0.0;
    hole_dist = 20.0;
    total_size = 25.0;
    inset = (total_size-hole_dist/2);
    hole_dia = 4.0;
    standoff_dia = 8.0;
    
    if (mode == "positive") {                
        // An outline that covers the whole area
        translate([total_size/2, total_size/2, 1-0.2]) color("red") cube([total_size, total_size, 0.2], center=false); 
        
        color("red") translate([inset, inset, -1]) cylinder(d=standoff_dia, h=2);
        color("red") translate([inset+hole_dist, inset, -1]) cylinder(d=standoff_dia, h=2);
        color("red") translate([inset, inset+hole_dist, -1]) cylinder(d=standoff_dia, h=2);
        color("red") translate([inset+hole_dist, inset+hole_dist, -1]) cylinder(d=standoff_dia, h=2);
        
    } else {   
        // TODO
        color("blue") translate([inset, inset, -1.1]) cylinder(d=hole_dia, h=6.5);
        color("blue") translate([inset+hole_dist, inset, -1.1]) cylinder(d=hole_dia, h=6.5);
        color("blue") translate([inset, inset+hole_dist, -1.1]) cylinder(d=hole_dia, h=6.5);
        color("blue") translate([inset+hole_dist, inset+hole_dist, -1.1]) cylinder(d=hole_dia, h=6.5);        
    }

} 

module mkSPS30Carrier() {
    
    sps30_size = 41.5;
    sps30_h = 12.5;
    
    // Bottom part, connects to main board
    difference() {
        color("purple") cube([8, 51.5, 5]);
        translate([8/2, 15, -1]) cylinder(h=10, d=2.5);
        translate([8/2, 15+20, -1]) cylinder(h=10, d=2.5);
        //translate([8/2, 15+40, -1]) cylinder(h=10, d=2.5);
    }
    
    h1 = 10-4; // height
    // Lifting section
    translate([7.5, 0, 0]) color("purple") cube([2, 51.5, h1]);
    
    
    camera_screw_dist = 21.0;
    difference() {
        // Flat plate
        union() {
            translate([7.5, 0, h1]) color("purple") cube([sps30_size-4, sps30_size+10, 6+sps30_h]);
            translate([7.5, -6, h1]) color("green") cube([sps30_size-4, 10, 4.5]);  // Extension
        }
        // sps30cutout
        translate([-2, 2.5, h1+2.5]) color("blue") cube([sps30_size, sps30_size, sps30_h+2]);
        // screw mounts for camera
        translate([14, sps30_size+6, h1+3.1+sps30_h-7+3]) cylinder(d=3.0, h=7);
        translate([14+camera_screw_dist, sps30_size+6, h1+3.1+sps30_h-7+3]) cylinder(d=3.0, h=7);
    
        // Cutout the back, so it's just a tab/stopper left at the back for the SPS30
        translate([-2.1+sps30_size, -2, h1+2.5+2]) color("blue") cube([20, sps30_size+15, 15]);
        
        // Thermal camera holes
        translate([sps30_size+1, sps30_size+6, h1-0.1]) cylinder(d=3.0, h=7);
        translate([sps30_size+1, sps30_size+6-50, h1-0.1]) cylinder(d=3.0, h=7);

    }     
    
    
    

    
    
}


// A faux SPS30 (just for sizing)
module mkFauxSPS30() {
    color("blue") cube([42, 42, 12]);
}


module camera_board_mount(
    insert_dia=3.5,
    insert_height=4.0,   // kept for compatibility, not used in current geometry
    thickness=4.0+3,
    border=3.0,
    thermal_dist_x=9,
    thermal_dist_y=50,
    usb_dist_x=25.0,
    usb_dist_y=25.0,
    usb_side_width=8.0,
    usb_extra_height=8.0,
    usb_standoff_dia_extra=2.5,
    usb_standoff_height=3.0,
    usb_mount_y_offset=3.0,
    fn_val=50,
    mode="positive"
) {
    $fn = fn_val;

    total_x = thermal_dist_x + (2 * border);
    total_y = thermal_dist_y + (2 * border);

    total_x_usb = usb_dist_x + (2 * border);
    total_y_usb = usb_dist_y + (2 * border);

    module mk_usb_camera_mount() {
        height = usb_extra_height + thickness;
        standoff_dia = insert_dia + usb_standoff_dia_extra;
        offset = (total_x_usb - usb_dist_x) / 2;

        difference() {
            union() {
                // Bottom
                cube([total_x_usb, total_y_usb, thickness]);

                // Sides
                translate([0, 0, 0])
                    cube([usb_side_width, total_y_usb, height]);
                translate([total_x_usb - usb_side_width, 0, 0]) {
                    difference() {
                        cube([usb_side_width, total_y_usb, height]);    // Side
                        translate([-1, 6, 0]) cube([usb_side_width+2, total_y_usb-6-6, height+1]);  // Take out the middle bits
                    }
                }

                // Standoffs
                translate([offset, offset, height - 7])
                    cylinder(h = 7.0 + usb_standoff_height, d = standoff_dia);
                translate([total_x_usb - offset, offset, height - 7])
                    cylinder(h = 7.0 + usb_standoff_height, d = standoff_dia);
                translate([offset, total_y_usb - offset, height - 7])
                    cylinder(h = 7.0 + usb_standoff_height, d = standoff_dia);
                translate([total_x_usb - offset, total_y_usb - offset, height - 7])
                    cylinder(h = 7.0 + usb_standoff_height, d = standoff_dia);
            }

            // Cutout screw mounts
            translate([offset, offset, height - 7])
                cylinder(h = 7.1 + usb_standoff_height, d = insert_dia);
            translate([total_x_usb - offset, offset, height - 7])
                cylinder(h = 7.1 + usb_standoff_height, d = insert_dia);
            translate([offset, total_y_usb - offset, height - 7])
                cylinder(h = 7.1 + usb_standoff_height, d = insert_dia);
            translate([total_x_usb - offset, total_y_usb - offset, height - 7])
                cylinder(h = 7.1 + usb_standoff_height, d = insert_dia);
        }
    }

    //difference() {
    if (mode == "positive") {
        union() {
            // Main part for the thermal camera
            translate([-1, -2, 0]) cube([total_x+2, total_y+2, thickness]);

            // USB camera mount
            translate([-(total_x_usb - total_x) / 2, (total_y / 2) + usb_mount_y_offset, 0])
                mk_usb_camera_mount();
        }
    } else if (mode == "negative") {
        // Thermal camera mounting holes
        translate([border, border-0.5, -1])
            cylinder(h = thickness + 2, d = insert_dia);
        translate([total_x - border, border-0.5, -1])
            cylinder(h = thickness + 2, d = insert_dia);
        translate([border, total_y - border-0.5, -1])
            cylinder(h = thickness + 2, d = insert_dia);
        translate([total_x - border, total_y - border-0.5, -1])
            cylinder(h = thickness + 2, d = insert_dia);
    }
}

module mkSpecMount(mode="positive") {
    screw_dist = 18.0;
    height = 3.5;
    connector_dist = 12.0;
    width = 6.0;
    
    screw_dia = 3.6; 
    
    if (mode == "positive") {
        cube([width, screw_dist+3+3, height]);
        
        //translate([-3.5+6.5, -3.5-7-0.1, -3.5+6]) color("green") cube([12, 15+0.2, 3.5+0.2]);     // Middle cutout
        //
    } else if (mode == "negative") {
        // Screws
        translate([width/2, 3, -1.5]) color("blue") cylinder(d=screw_dia, h=5.1);
        translate([width/2, screw_dist+3, -1.5]) color("blue") cylinder(d=screw_dia, h=5.1);
        // Middle Cutout
        translate([-1, 6, -0]) color("green") cube([width+6, screw_dist-screw_dia-2, height+3.1]);
    }
    
}

module slanting_cube(size_x_bottom, size_x_top, size_y, size_z) {
    eps = 0.001;
    x_shift = size_x_bottom - size_x_top;   // makes the top extend in negative X

    hull() {
        cube([size_x_bottom, size_y, eps]);

        translate([x_shift, 0, size_z - eps])
            cube([size_x_top, size_y, eps]);
    }
}

module mkSensorBoardMountVertical(mode="positive") {
    board_length = 27.0;
    board_thickness = 2.5;
    sunk_depth = 5.0;
    hole_dia = 4.0;
    hole_dist = 20.0;
    
    hole_offset_x = (board_length-hole_dist)/2; // Distance from edge to hole center
    hole_offset_y = 23.0 - sunk_depth;  // Distance from the non-sunk part to the hole center
    height_above_sunk = board_length - sunk_depth;
    
    back_thickness = 2.5;
    
    // Back plate
    if (mode == "positive") {
        difference() {
            union() {
                color("blue") slanting_cube(back_thickness, back_thickness+2, board_length, height_above_sunk-6);
                color("blue") translate([-2, 0, height_above_sunk-6]) cube([back_thickness+2, board_length, 6]);
            }
            // Screw cutouts
            color("purple") translate([-3, hole_offset_x, hole_offset_y]) rotate([0, 90, 0]) cylinder(h=back_thickness+2+2, d=hole_dia);
            color("purple") translate([-3, hole_offset_x + hole_dist, hole_offset_y]) rotate([0, 90, 0]) cylinder(h=back_thickness+2+2, d=hole_dia);
        }

        // Measurement gauge (7mm) (TEMPORARY)
        //color("purple") translate([back_thickness, 0, 0]) cube([7, 1, 1]);
     
    } else if (mode == "negative") {

        // Sunk part (cutout)
        color("red") translate([back_thickness, 0, -sunk_depth]) cube([board_thickness, board_length, sunk_depth+0.1]);
    }
          
}


module mkSPS30Cutout(mode="positive") {
    sps30_size = 41.5;
    sps30_h = 12.5;
    
    // The cutout itself
    if (mode == "positive") {
        
    } else if (mode == "negative") {
        color("blue") cube([sps30_size, sps30_size, sps30_h]);
    }
    
}


module magneticTileHolder() {
    tileSizeX = 52.5;
    tileSizeY = 35.0;
    
    tileScrewDist = 29.5;   // Distance between screws (Y axis)
    tileScrewOffset = 2.7;  // Distance from the edge of the board, to the center of the screw. 
    
    tileTotalHeight = 8.0;  // Total height, including external connector
    
    VERSION = "v1a";
    
    
    // Main
    
    borderSize = 2.0;
    bottomSize = 1.5;
    
    totalWidth = tileSizeX + (2*borderSize);
    totalLength = tileSizeY + (2*borderSize);
    
    totalHeight = tileTotalHeight + borderSize; // Don't include the border on the top for this design
    
    lipSize = 1.0;
    lipHeight = 0.5;
    
    boardLipHeight = 3.4;
    brassInsertDia = 4.0;
    insertOffsetY = (totalLength - tileScrewDist)/2;
    
    difference() {
        union() {
            difference() {
            // Main outline
                union() {
                    cube([totalWidth, totalLength, totalHeight]); 
                    // Brass Inserts
                }
                // Cut out internal cube
                translate([borderSize, borderSize, bottomSize]) cube([tileSizeX, tileSizeY, tileTotalHeight+0.1]);
        
                // Cut out a lip at the top
                translate([lipSize, lipSize, totalHeight-lipHeight]) color("red") cube([totalWidth-(2*lipSize), totalLength-(2*lipSize), lipHeight+0.1]); 
           
            }
            
            //## Add a back
            back_thickness = 2.0;
            difference () {
                union () {
                translate([0, 0, -2]) color("blue") cube([56.5, 39, back_thickness]); // 2mm back on the whole thing            
                translate([0, 10, -2]) color("purple") linear_extrude(height = 3.5) roundedRect2D(90+3, 20, r=5);  // 5mm corner radius 
                //translate([56.5+32, 13+(14/2), -3]) cylinder(h=7, d=2.5); // Screw hole
                //translate([56.5-10, 5, -3]) cylinder(h=4.5+1, d=3.5); // Screw hole
                //translate([56.5-40, 5, -3]) cylinder(h=4.5+1, d=3.5); // Screw hole
                }
                
                // slot on the back for air
                translate([-0.1, 12, -3]) color("red") cube([56.5+12.1, 15, back_thickness+1]); 
                // inlet
                translate([56.5+20, 13, -2.1]) color("red") linear_extrude(height = 5.1) roundedRect2D(7, 14, r=2);
                // Screw hole
                translate([56.5+32, 13+(14/2), -3]) cylinder(h=7, d=2.5); // Screw hole                
            }
            
    
            // Add a lip for the board on the side
            translate([0, borderSize, 0]) color("blue") cube([totalWidth, 1.5, totalHeight-boardLipHeight]); 
            translate([0, totalLength-borderSize-1.5, 0]) color("blue") cube([totalWidth, 1.5, totalHeight-boardLipHeight]); 
    
            // Add some brass inserts
            translate([totalWidth - borderSize - 2.7, insertOffsetY, 0]) {
                difference() {
                    cylinder(d=brassInsertDia+2.5, h=5); 
                    //cylinder(d=brassInsertDia, h=5+0.1); 
                }
            }
    
            translate([totalWidth - borderSize - 2.7, insertOffsetY + tileScrewDist, 0]) {
                difference() {
                    cylinder(d=brassInsertDia+2.5, h=5); 
                    //cylinder(d=brassInsertDia, h=5+0.1); 
                }
            }
                        
        }
    
        // Insert holes (to main case)
        translate([56.5-10, 5, -3]) cylinder(h=4.5+1, d=3.5); // Screw hole
        translate([56.5-40, 5, -3]) cylinder(h=4.5+1, d=3.5); // Screw hole
        
        // Add some brass inserts (internal)
        translate([totalWidth - borderSize - 2.7, insertOffsetY, 0.6]) {
            difference() {
                //cylinder(d=brassInsertDia+2.5, h=5); 
                cylinder(d=brassInsertDia, h=2*5); 
            }
        }
    
        translate([totalWidth - borderSize - 2.7, insertOffsetY + tileScrewDist, 0.6]) {
            difference() {
                //cylinder(d=brassInsertDia+2.5, h=5); 
                cylinder(d=brassInsertDia, h=2*5); 
            }
        }
    
        // Hole for the cables to come out of the bottom
        offsetX = 16.0;
        translate([totalWidth - offsetX - 5, (totalLength/2) - (12/2), -0.1]) cube([5, 12, bottomSize+2]);
    }
    
    
    // Add some nubs for the magnetometer to align with
    nubDia = 3.2;
    nubHeight = 1.5;
    nubDist = 20.0;
    
    nubOffsetX = 7.0;
    nubOffsetY = 5.0;
    
    nubX = borderSize + nubOffsetX;
    nubY = borderSize + nubOffsetY;
    // Nub 1
    translate([nubX, nubY, bottomSize]) color("green") cylinder(d=nubDia, h=nubHeight); 
    // Nub 2
    translate([nubX, nubY+nubDist, bottomSize]) color("green") cylinder(d=nubDia, h=nubHeight); 
    
    // Add version text
    translate([totalWidth/2 + 7, totalLength/2 - 15, bottomSize]) linear_extrude(0.1) text(VERSION, size=4);
    

}



module magneticTileHolder1() {
    tileSizeX = 52.5+0.5;
    tileSizeY = 35.0+0.5;
    
    tileScrewDist = 29.5;   // Distance between screws (Y axis)
    tileScrewOffset = 2.7;  // Distance from the edge of the board, to the center of the screw. 
    
    tileTotalHeight = 8.0+1;  // Total height, including external connector
    
    VERSION = "v1a";
    
    
    // Main
    
    borderSize = 2.0;
    bottomSize = 1.5;
    
    totalWidth = tileSizeX + (2*borderSize);
    totalLength = tileSizeY + (2*borderSize);
    
    totalHeight = tileTotalHeight + borderSize; // Don't include the border on the top for this design
    
    lipSize = 1.0;
    lipHeight = 0.5-0.2;
    
    boardLipHeight = 1;
    brassInsertDia = 4.0;
    insertOffsetY = (totalLength - tileScrewDist)/2;
    

    
    difference() {
        union() {
            difference() {
            // Main outline
                union() {
                    cube([totalWidth, totalLength, totalHeight]); 
                    // Brass Inserts
                }
                // Cut out internal cube
                translate([borderSize, borderSize, -1.5]) cube([tileSizeX, tileSizeY, totalHeight+0.1]);
                    
                // Cut out magnetometer tile Aperture
                translate([borderSize+2, borderSize+1.5+0.25+0.5, 0.5]) color("red") cube([32, 32-1, 10+1]);
                // Cut out magnetometer tile Aperture
                translate([borderSize+2-1, borderSize+1+0.25+0.5, -0.6]) color("red") cube([35, 33-1, 10+1]);

                // Cut out space for larger ICs
                translate([borderSize+2+38, borderSize+1+0.75, -0.75]) color("red") cube([10, 32, 10+1]);
                
                // Cut out a lip at the top
                //translate([lipSize, lipSize, totalHeight-lipHeight]) color("red") cube([totalWidth-(2*lipSize), totalLength-(2*lipSize), lipHeight+0.1]); 

// Holes for side screws
                
                // Screw block (1)
                translate([0-1, borderSize+(tileSizeY/2)-3, 1.25]) {                                
                    translate([-1, 6/2, 5/2]) rotate([0, 90, 0]) color("purple") cylinder(d=2.5, h=6);                    
                }
                
                /*
                // Screw block (2)            
                translate([borderSize+tileSizeX, borderSize+(tileSizeY/2)-3, 1.25]) {
                    translate([-1, 6/2, 5/2]) rotate([0, 90, 0]) color("purple") cylinder(d=2.5, h=6);
                }
//                */


                // Cut out a slot for the longer mating part to extend out of
                translate([5+0.1, 10, -2]) color("purple") linear_extrude(height = 3.5+0.1) roundedRect2D(90, 20.2, r=5);  // 5mm corner radius 

                // Screw block (3)            
                translate([borderSize+tileSizeX-4-borderSize-0.1, borderSize+0.1-5, 1.5]) {                        
                    translate([6/2, 0, 5/2]) rotate([0, 90, 90]) color("purple") cylinder(d=2.5, h=6);
                }

                // Screw block (4)            
                translate([borderSize+tileSizeX-4-borderSize-0.1, borderSize+tileSizeY-0.1, 1.5]) {
                    translate([6/2, 0, 5/2]) rotate([0, 90, 90]) color("purple") cylinder(d=2.5, h=6);
                }
           
            }

            
            
            /*
            //## Add a back
            back_thickness = 2.0;
            difference () {
                union () {
                translate([0, 0, -2]) color("blue") cube([56.5, 39, back_thickness]); // 2mm back on the whole thing            
                translate([0, 10, -2]) color("purple") linear_extrude(height = 3.5) roundedRect2D(90+3, 20, r=5);  // 5mm corner radius 
                //translate([56.5+32, 13+(14/2), -3]) cylinder(h=7, d=2.5); // Screw hole
                //translate([56.5-10, 5, -3]) cylinder(h=4.5+1, d=3.5); // Screw hole
                //translate([56.5-40, 5, -3]) cylinder(h=4.5+1, d=3.5); // Screw hole
                }
                
                // slot on the back for air
                translate([-0.1, 12, -3]) color("red") cube([56.5+12.1, 15, back_thickness+1]); 
                // inlet
                translate([56.5+20, 13, -2.1]) color("red") linear_extrude(height = 5.1) roundedRect2D(7, 14, r=2);
                // Screw hole
                translate([56.5+32, 13+(14/2), -3]) cylinder(h=7, d=2.5); // Screw hole                
            }
            */
            
    
            // Add a lip for the board on the side
            translate([0, borderSize, 7.5+1+0.1]) color("blue") cube([totalWidth, 1.5, boardLipHeight]); 
            translate([0, totalLength-borderSize-1.5, 7.5+1+0.1]) color("blue") cube([totalWidth, 1.5, boardLipHeight]); 
    
    /*
            // Add some brass inserts
            translate([totalWidth - borderSize - 2.7, insertOffsetY, 0]) {
                difference() {
                    cylinder(d=brassInsertDia+2.5, h=5); 
                    //cylinder(d=brassInsertDia, h=5+0.1); 
                }
            }    
            translate([totalWidth - borderSize - 2.7, insertOffsetY + tileScrewDist, 0]) {
                difference() {
                    cylinder(d=brassInsertDia+2.5, h=5); 
                    //cylinder(d=brassInsertDia, h=5+0.1); 
                }
            }
   */
        }
    
        
        // Insert holes (to main case)
        translate([56.5-10, 5, -3]) cylinder(h=4.5+1, d=3.5); // Screw hole
        translate([56.5-40, 5, -3]) cylinder(h=4.5+1, d=3.5); // Screw hole
        
        /*
        // Add some brass inserts (internal)
        translate([totalWidth - borderSize - 2.7, insertOffsetY, 0.6]) {
            difference() {
                //cylinder(d=brassInsertDia+2.5, h=5); 
                cylinder(d=brassInsertDia, h=2*5); 
            }
        }
    
        translate([totalWidth - borderSize - 2.7, insertOffsetY + tileScrewDist, 0.6]) {
            difference() {
                //cylinder(d=brassInsertDia+2.5, h=5); 
                cylinder(d=brassInsertDia, h=2*5); 
            }
        }
        */
    
        // Hole for the cables to come out of the bottom
        offsetX = 16.0;
        translate([totalWidth - offsetX - 5, (totalLength/2) - (12/2), -0.1]) cube([5, 12, bottomSize+2]);
    }
    
    
    // Add some nubs for the magnetometer to align with
    nubDia = 3.2;
    nubHeight = 1.5;
    nubDist = 20.0;
    
    nubOffsetX = 7.0;
    nubOffsetY = 5.0;
    
    nubX = borderSize + nubOffsetX;
    nubY = borderSize + nubOffsetY;
    // Nubs for the magnetometer board
    /*
    // Nub 1
    translate([nubX, nubY, bottomSize]) color("green") cylinder(d=nubDia, h=nubHeight); 
    // Nub 2
    translate([nubX, nubY+nubDist, bottomSize]) color("green") cylinder(d=nubDia, h=nubHeight); 
    
    // Add version text
    translate([totalWidth/2 + 7, totalLength/2 - 15, bottomSize]) linear_extrude(0.1) text(VERSION, size=4);
    */
    

}


module magneticTileHolder1a() {
    tileSizeX = 52.5+0.5;
    tileSizeY = 35.0+0.5;
    
    tileScrewDist = 29.5;   // Distance between screws (Y axis)
    tileScrewOffset = 2.7;  // Distance from the edge of the board, to the center of the screw. 
    
    tileTotalHeight = 8.0;  // Total height, including external connector
    
    VERSION = "v1a";
    
    
    // Main
    
    borderSize = 2.0;
    bottomSize = 1.5;
    
    totalWidth = tileSizeX + (2*borderSize);
    totalLength = tileSizeY + (2*borderSize);
    
    totalHeight = tileTotalHeight + borderSize; // Don't include the border on the top for this design
    
    lipSize = 1.0;
    lipHeight = 0.5-0.2;
    
    boardLipHeight = 1;
    brassInsertDia = 4.0;
    insertOffsetY = (totalLength - tileScrewDist)/2;
    

    
    difference() {
        union() {
            /*
            difference() {
            // Main outline
                union() {
                    cube([totalWidth, totalLength, totalHeight]); 
                    // Brass Inserts
                }
                // Cut out internal cube
                translate([borderSize, borderSize, -1.5]) cube([tileSizeX, tileSizeY, totalHeight+0.1]);
                    
                // Cut out magnetometer tile Aperture
                translate([borderSize+2, borderSize+1.5+0.25, 0.5]) color("red") cube([32, 32, 10]);
                // Cut out magnetometer tile Aperture
                translate([borderSize+2-1, borderSize+1+0.25, -0.6]) color("red") cube([35, 33, 10]);

                // Cut out space for larger ICs
                translate([borderSize+2+38, borderSize+1, -0.75]) color("red") cube([10, 33, 10]);


                
                // Cut out a lip at the top
                //translate([lipSize, lipSize, totalHeight-lipHeight]) color("red") cube([totalWidth-(2*lipSize), totalLength-(2*lipSize), lipHeight+0.1]); 
           
            }
            */
            
            
            //## Add a back
            back_thickness = 2.0;
            difference () {
                union () {
                translate([0, 0, -2]) color("blue") cube([56.5+0.5, 39, back_thickness]); // 2mm back on the whole thing            
                // inside lip
                translate([borderSize+0.1, borderSize+0.1, 0]) color("blue") cube([56.5+0.5-(2*borderSize)-0.2, 39-(2*borderSize)-0.2, 2]); // 2mm back on the whole thing            
                    
                // Screw block (1)
                translate([borderSize+0.1, borderSize+(tileSizeY/2)-3, 1.25]) {
                    difference() {
                    color("red") cube([4, 6, 5+0.5]); // 2mm back on the whole thing            
                    translate([-1, 6/2, 5/2]) rotate([0, 90, 0]) color("purple") cylinder(d=3.6, h=6);
                    }
                }
                
                /*
                // Screw block (2)            
                translate([borderSize+tileSizeX-4-0.1, borderSize+(tileSizeY/2)-3, 1.25]) {                    
                    difference() {
                    color("red") cube([4, 6, 5]); // 2mm back on the whole thing            
                    translate([-1, 6/2, 5/2]) rotate([0, 90, 0]) color("purple") cylinder(d=3.6, h=6);
                    }
                }
                */

                // Screw block (3)            
                translate([borderSize+tileSizeX-4-borderSize-0.1, borderSize+0.1, 1.25]) {                    
                    difference() {
                    color("red") cube([6, 4, 5+0.5]); // 2mm back on the whole thing            
                    translate([6/2, -1, 5/2]) rotate([0, 90, 90]) color("purple") cylinder(d=3.6, h=6);
                    }
                }

                // Screw block (4)            
                translate([borderSize+tileSizeX-4-borderSize-0.1, borderSize+tileSizeY-4.5-0.1, 1.25]) {
                    difference() {
                    color("red") cube([6, 4, 5+0.5]); // 2mm back on the whole thing            
                    translate([6/2, -1, 5/2]) rotate([0, 90, 90]) color("purple") cylinder(d=3.6, h=6);
                    }
                }
                    
                // Purple length
                translate([3, 10, -2]) color("purple") linear_extrude(height = 3.5) roundedRect2D(90, 20, r=5);  // 5mm corner radius 
                //translate([56.5+32, 13+(14/2), -3]) cylinder(h=7, d=2.5); // Screw hole
                //translate([56.5-10, 5, -3]) cylinder(h=4.5+1, d=3.5); // Screw hole
                //translate([56.5-40, 5, -3]) cylinder(h=4.5+1, d=3.5); // Screw hole
                }
                
                // slot on the back for air
                translate([-0.1, 12, -3]) color("red") cube([56.5+12.1, 15, back_thickness+1]); 
                // inlet
                translate([56.5+20, 13, -2.1]) color("red") linear_extrude(height = 5.1) roundedRect2D(7, 14, r=2);
                // Screw hole
                translate([56.5+32, 13+(14/2), -3]) cylinder(h=7, d=2.5); // Screw hole                
            }
            
            // Holder for the power switch 
            difference () {
            union() {
                translate([12, 39, -2]) color("green") cube([10+4, 9, back_thickness]);
                translate([12, 39+0.2, -2]) color("green") cube([10+4, 9-0.2, back_thickness+2]);
            }
            // Now, make a hole through it
            translate([12+2, 39, -2-0.5]) color("purple") cube([10, 2.5+2+2, back_thickness+2+1]);
            }
            
            
    
            // Add a lip for the board on the side
            //translate([0, borderSize, 7.5+0.1]) color("blue") cube([totalWidth, 1.0, boardLipHeight]); 
            //translate([0, totalLength-borderSize-1, 7.5+0.1]) color("blue") cube([totalWidth, 1.0, boardLipHeight]); 
    
    /*
            // Add some brass inserts
            translate([totalWidth - borderSize - 2.7, insertOffsetY, 0]) {
                difference() {
                    cylinder(d=brassInsertDia+2.5, h=5); 
                    //cylinder(d=brassInsertDia, h=5+0.1); 
                }
            }    
            translate([totalWidth - borderSize - 2.7, insertOffsetY + tileScrewDist, 0]) {
                difference() {
                    cylinder(d=brassInsertDia+2.5, h=5); 
                    //cylinder(d=brassInsertDia, h=5+0.1); 
                }
            }
   */
        }
    
        
        // Insert holes (to main case)
        translate([56.5-10, 5, -3]) cylinder(h=4.5+1, d=3.5); // Screw hole
        translate([56.5-40, 5, -3]) cylinder(h=4.5+1, d=3.5); // Screw hole
        
        /*
        // Add some brass inserts (internal)
        translate([totalWidth - borderSize - 2.7, insertOffsetY, 0.6]) {
            difference() {
                //cylinder(d=brassInsertDia+2.5, h=5); 
                cylinder(d=brassInsertDia, h=2*5); 
            }
        }
    
        translate([totalWidth - borderSize - 2.7, insertOffsetY + tileScrewDist, 0.6]) {
            difference() {
                //cylinder(d=brassInsertDia+2.5, h=5); 
                cylinder(d=brassInsertDia, h=2*5); 
            }
        }
        */
    
        // Hole for the cables to come out of the bottom
        offsetX = 16.0;
        translate([totalWidth - offsetX - 5, (totalLength/2) - (12/2), -0.1]) cube([5, 12, bottomSize+2]);
    }
    
    
    // Add some nubs for the magnetometer to align with
    nubDia = 3.2;
    nubHeight = 2.25;
    nubDist = 20.5;
    
    nubOffsetX = 7.0;
    nubOffsetY = 5.0;
    
    nubX = borderSize + nubOffsetX;
    nubY = borderSize + nubOffsetY;
    // Nubs for the magnetometer board
    
    // Nub 1
    translate([nubX+0.5, nubY, bottomSize]) color("green") cylinder(d=nubDia, h=nubHeight); 
    // Nub 2
    translate([nubX+0.5, nubY+nubDist, bottomSize]) color("green") cylinder(d=nubDia, h=nubHeight); 
    
    // Add version text
    //translate([totalWidth/2 + 7, totalLength/2 - 15, bottomSize]) linear_extrude(0.1) text(VERSION, size=4);
    
    

}



module magneticTileHolder1Grid() {
    tileSizeX = 52.5+0.5;
    tileSizeY = 35.0+0.5;
    
    tileScrewDist = 29.5;   // Distance between screws (Y axis)
    tileScrewOffset = 2.7;  // Distance from the edge of the board, to the center of the screw. 
    
    tileTotalHeight = 8.0+1;  // Total height, including external connector
    
    VERSION = "v1a";
    
    
    // Main
    
    borderSize = 2.0;
    bottomSize = 1.5;
    
    totalWidth = tileSizeX + (2*borderSize);
    totalLength = tileSizeY + (2*borderSize);
    
    totalHeight = tileTotalHeight + borderSize; // Don't include the border on the top for this design
    
    lipSize = 1.0;
    lipHeight = 0.5-0.2;
    
    boardLipHeight = 1;
    brassInsertDia = 4.0;
    insertOffsetY = (totalLength - tileScrewDist)/2;
    

    
    difference() {
        union() {
            difference() {
            // Main outline
                union() {
                    cube([totalWidth, totalLength, totalHeight]); 
                    // Brass Inserts
                }
                // Cut out internal cube
                translate([borderSize, borderSize, -1.5]) cube([tileSizeX, tileSizeY, totalHeight+0.1]);
                    
                // Cut out magnetometer tile Aperture
                translate([borderSize+2, borderSize+1.5+0.25+0.5, 0.5]) color("red") cube([32, 32-1, 10+1]);
                // Cut out magnetometer tile Aperture
                translate([borderSize+2-1, borderSize+1+0.25+0.5, -0.6]) color("red") cube([35, 33-1, 10+1]);

                // Cut out space for larger ICs
                translate([borderSize+2+38, borderSize+1+0.75, -0.75]) color("red") cube([10, 32, 10+1]);
                
                // Cut out a lip at the top
                //translate([lipSize, lipSize, totalHeight-lipHeight]) color("red") cube([totalWidth-(2*lipSize), totalLength-(2*lipSize), lipHeight+0.1]); 

// Holes for side screws
                
                // Screw block (1)
                translate([0-1, borderSize+(tileSizeY/2)-3, 1.25]) {                                
                    translate([-1, 6/2, 5/2]) rotate([0, 90, 0]) color("purple") cylinder(d=2.5, h=6);                    
                }
                
                /*
                // Screw block (2)            
                translate([borderSize+tileSizeX, borderSize+(tileSizeY/2)-3, 1.25]) {
                    translate([-1, 6/2, 5/2]) rotate([0, 90, 0]) color("purple") cylinder(d=2.5, h=6);
                }
//                */


                // Cut out a slot for the longer mating part to extend out of
                translate([5+0.1, 10, -2]) color("purple") linear_extrude(height = 3.5+0.1) roundedRect2D(90, 20.2, r=5);  // 5mm corner radius 

                // Screw block (3)            
                translate([borderSize+tileSizeX-4-borderSize-0.1, borderSize+0.1-5, 1.5]) {                        
                    translate([6/2, 0, 5/2]) rotate([0, 90, 90]) color("purple") cylinder(d=2.5, h=6);
                }

                // Screw block (4)            
                translate([borderSize+tileSizeX-4-borderSize-0.1, borderSize+tileSizeY-0.1, 1.5]) {
                    translate([6/2, 0, 5/2]) rotate([0, 90, 90]) color("purple") cylinder(d=2.5, h=6);
                }
           
            }
            
            translate([borderSize+2+1, borderSize+1.5+0.25+0.5+1, totalHeight-0.5]) color("red") cube([32-2, 32-1-2, 0.5]);
            translate([borderSize+1, borderSize+1.5+0.25, totalHeight-1]) color("purple") cube([32+3, 32-1+3, 0.5]);

            
            
            /*
            //## Add a back
            back_thickness = 2.0;
            difference () {
                union () {
                translate([0, 0, -2]) color("blue") cube([56.5, 39, back_thickness]); // 2mm back on the whole thing            
                translate([0, 10, -2]) color("purple") linear_extrude(height = 3.5) roundedRect2D(90+3, 20, r=5);  // 5mm corner radius 
                //translate([56.5+32, 13+(14/2), -3]) cylinder(h=7, d=2.5); // Screw hole
                //translate([56.5-10, 5, -3]) cylinder(h=4.5+1, d=3.5); // Screw hole
                //translate([56.5-40, 5, -3]) cylinder(h=4.5+1, d=3.5); // Screw hole
                }
                
                // slot on the back for air
                translate([-0.1, 12, -3]) color("red") cube([56.5+12.1, 15, back_thickness+1]); 
                // inlet
                translate([56.5+20, 13, -2.1]) color("red") linear_extrude(height = 5.1) roundedRect2D(7, 14, r=2);
                // Screw hole
                translate([56.5+32, 13+(14/2), -3]) cylinder(h=7, d=2.5); // Screw hole                
            }
            */
            
    
            // Add a lip for the board on the side
            translate([0, borderSize, 7.5+1+0.1]) color("blue") cube([totalWidth, 1.5, boardLipHeight]); 
            translate([0, totalLength-borderSize-1.5, 7.5+1+0.1]) color("blue") cube([totalWidth, 1.5, boardLipHeight]); 
    
    /*
            // Add some brass inserts
            translate([totalWidth - borderSize - 2.7, insertOffsetY, 0]) {
                difference() {
                    cylinder(d=brassInsertDia+2.5, h=5); 
                    //cylinder(d=brassInsertDia, h=5+0.1); 
                }
            }    
            translate([totalWidth - borderSize - 2.7, insertOffsetY + tileScrewDist, 0]) {
                difference() {
                    cylinder(d=brassInsertDia+2.5, h=5); 
                    //cylinder(d=brassInsertDia, h=5+0.1); 
                }
            }
   */
        }
    
        
        // Insert holes (to main case)
        translate([56.5-10, 5, -3]) cylinder(h=4.5+1, d=3.5); // Screw hole
        translate([56.5-40, 5, -3]) cylinder(h=4.5+1, d=3.5); // Screw hole
        
        /*
        // Add some brass inserts (internal)
        translate([totalWidth - borderSize - 2.7, insertOffsetY, 0.6]) {
            difference() {
                //cylinder(d=brassInsertDia+2.5, h=5); 
                cylinder(d=brassInsertDia, h=2*5); 
            }
        }
    
        translate([totalWidth - borderSize - 2.7, insertOffsetY + tileScrewDist, 0.6]) {
            difference() {
                //cylinder(d=brassInsertDia+2.5, h=5); 
                cylinder(d=brassInsertDia, h=2*5); 
            }
        }
        */
    
        // Hole for the cables to come out of the bottom
        offsetX = 16.0;
        translate([totalWidth - offsetX - 5, (totalLength/2) - (12/2), -0.1]) cube([5, 12, bottomSize+2]);
    }
    
    
    // Add some nubs for the magnetometer to align with
    nubDia = 3.2;
    nubHeight = 1.5;
    nubDist = 20.0;
    
    nubOffsetX = 7.0;
    nubOffsetY = 5.0;
    
    nubX = borderSize + nubOffsetX;
    nubY = borderSize + nubOffsetY;
    // Nubs for the magnetometer board
    /*
    // Nub 1
    translate([nubX, nubY, bottomSize]) color("green") cylinder(d=nubDia, h=nubHeight); 
    // Nub 2
    translate([nubX, nubY+nubDist, bottomSize]) color("green") cylinder(d=nubDia, h=nubHeight); 
    
    // Add version text
    translate([totalWidth/2 + 7, totalLength/2 - 15, bottomSize]) linear_extrude(0.1) text(VERSION, size=4);
    */
    

}




module main() {
// Main
    
    difference() {
        difference() {
            union () {
                difference() {
                    mkBack();
                    translate([100-7-5, 75-7, 8]) mkESP32MountPattern(mode="precut");
                }
                /*
                // Spectrometer
                translate([62, 150+3, 0]) {
                    mkSpecMountPattern(mode="positive");
                }            
                // Camera
                translate([60+2, 120, 0]) {
                    mkCameraMountPattern(mode="positive");
                }
                */
                /*
                // Air particle
                translate([86-1, 120, 0]) {
                    mkAirParticleSensorMountPattern(mode="positive");
                }
                */
                
                /*
                // CM5 cooler
                translate([width-18-60, length-35-45, 0]) {
                    mkCM5CoolerPattern();
                }
                */
                
                // ESP32 Mount Pattern                
                translate([100-7-5, 75-7, 10]) mkESP32MountPattern(mode="positive");
                            
                // QWIIC board mount patterns
                //translate([100-17, 75+27, -1]) mkSparkfunGenericQWIICBoardMountPattern(mode="positive");
                //translate([100-17, 75-7, -1]) mkSparkfunGenericQWIICBoardMountPattern(mode="positive");
                            
                translate([116.5, 86, 4]) rotate([0, 180, 0]) color("blue") camera_board_mount(mode="positive");
//                translate([100, 75, -15]) mkFauxSPS30();
//                translate([10, 75, -15]) mkFauxSPS30();

                // Spectrometer mount
                translate([102.0, 149, 2]) rotate([0, 180, 0]) color("red") mkSpecMount(mode="positive");         
         
                // Sensor board (vertical)
                //translate([10.5, 130+2, -0]) rotate([0, 180, 0]) mkSensorBoardMountVertical(mode="positive");                
                //translate([10.5, 130+2-43-27, -0]) rotate([0, 180, 0]) mkSensorBoardMountVertical(mode="positive");
                
                // SPS30 
                //translate([50, 150-16, -12.5]) mkSPS30Cutout(mode="positive");
                
                // Holes for magnetic tile mount on the front                
                // Block for an insert hole (from magnetic tile)
                translate([width-90+1.5-4+0.5, length-5, -10]) color("red") cube([8, 5, 10]); 
                // Another block, to keep the small tab near the SPS30 from breaking away
                translate([width-43.5, length-5, -13]) color("red") cube([3.5, 4, 13]); 
                
                // SPS30: Small hole to cover the top inlet aperture, to try to draw air just from outside
                translate([width-90+1.5-4+0.5, length-5, -13]) color("red") cube([25, 3, 10]); 
                
                // USB hub standoffs
                translate([(width/2)+15-8, 6+0.5, -0.1]) {
                    rotate([0, 0, 90]) mkUSBHubMountPattern(mode="positive");      
                }  
             

            }
            
        
            // Make a cutout along most of the back
            cutout_width = width - 10.0;
            cutout_length = length - 30.0;
            cutout_depth = 4.0;
                
            translate([5, 15, thickness-cutout_depth+0.1]) {
                color("purple") cube([cutout_width, cutout_length, cutout_depth]);
            }
        }
       
           // Add some spaces for screw mounts
        
        // Beside Pomello
        mhil = 7.0; // Mount hole inset length (distance from the edge)
        //translate([mhil, 90-2+(20*0), -0.1]) color("blue") cylinder(d=4, h=5);
        //translate([mhil, 90-2+(20*1), -0.1]) color("blue") cylinder(d=4, h=5);
        //translate([mhil, 90-2+(20*2), -0.1]) color("blue") cylinder(d=4, h=5);
        //translate([mhil, 90-2+(20*3), -0.1]) color("blue") cylinder(d=4, h=5);
        
        //translate([mhil, 90-2+(20*-1), -0.1]) color("blue") cylinder(d=4, h=5);
        translate([mhil, 90-2+(20*-2), -0.1]) color("blue") cylinder(d=4, h=5);
        translate([mhil, 90-2+(20*-3), -0.1]) color("blue") cylinder(d=4, h=5);
        //translate([8, 90-2+(20*-4), -0.1]) color("blue") cylinder(d=4, h=5);
        //translate([8, 90-2+(20*-5), -0.1]) color("blue") cylinder(d=4, h=5);

        // Opposite side from Pomello
        translate([width-mhil, 90-2+(20*0), -0.1]) color("blue") cylinder(d=4, h=5);
        translate([width-mhil, 90-2+(20*1), -0.1]) color("blue") cylinder(d=4, h=5);
        translate([width-mhil, 90-2+(16*-1), -0.1]) color("blue") cylinder(d=4, h=5);

        translate([width-mhil-30, 90-2+(20*0), -0.1]) color("blue") cylinder(d=4, h=5);
        translate([width-mhil-30, 90-2+(20*1), -0.1]) color("blue") cylinder(d=4, h=5);
        translate([width-mhil-30, 90-2+(16*-1), -0.1]) color("blue") cylinder(d=4, h=5);

        
        // Bottom
        //translate([8+45+(20*-2), 90-2+(20*-4), -0.1]) color("blue") cylinder(d=4, h=5);
        translate([mhil+45+(20*-1), 90-2+(20*-4), -0.1]) color("blue") cylinder(d=4, h=5);
        //translate([mhil+45+(20*0), 90-2+(20*-4), -0.1]) color("blue") cylinder(d=4, h=5);
        //translate([mhil+45+(20*1), 90-2+(20*-4), -0.1]) color("blue") cylinder(d=4, h=5);
        //translate([mhil+45+(20*2), 90-2+(20*-4), -0.1]) color("blue") cylinder(d=4, h=5);
        //translate([mhil+45+(20*3), 90-2+(20*-4), -0.1]) color("blue") cylinder(d=4, h=5);
        
        // Beside battery
        //translate([mhil+45+(20*0), 90-2-16, -0.1]) color("blue") cylinder(d=4, h=5);
        //translate([mhil+45+(20*1), 90-2-16, -0.1]) color("blue") cylinder(d=4, h=5);
        //translate([mhil+45+(20*2), 90-2-16, -0.1]) color("blue") cylinder(d=4, h=5);
        //translate([mhil+45+(20*3), 90-2-16, -0.1]) color("blue") cylinder(d=4, h=5);
        // In front of ESP32
        //translate([mhil+35+(20*0)-1, 155-3, -0.1]) color("blue") cylinder(d=4, h=5);        
        translate([mhil+35+(50)-2, 155-3, -0.1]) color("blue") cylinder(d=4, h=5);
        translate([mhil+35+(50)-2, 155-3-10, -0.1]) color("blue") cylinder(d=4, h=5);

        //translate([mhil+35+(20*0)-1, 155-3-10, -0.1]) color("blue") cylinder(d=4, h=5);        
        //translate([mhil+35+(20*0)-1, 165-3, -0.1]) color("blue") cylinder(d=4, h=5);        
        //translate([mhil+35+(50)-2, 170-1, -0.1]) color("blue") cylinder(d=4, h=5); // front, near magtile cable aperture

        translate([mhil+67+(50)-2, 155-3, -0.1]) color("blue") cylinder(d=4, h=5);
        
        // Very front
        //translate([mhil+45+(20*0), 170-2, -0.1]) color("blue") cylinder(d=4, h=5);
        //translate([mhil+45+(20*1), 170-2, -0.1]) color("blue") cylinder(d=4, h=5);
        //translate([mhil+45+(20*2), 170-2, -0.1]) color("blue") cylinder(d=4, h=5);
        //translate([mhil+45+(20*3), 170-2, -0.1]) color("blue") cylinder(d=4, h=5);
    
        /*    
        // CM5 cooler
        translate([width-18-60, length-35-45, 0]) {
            mkCM5CoolerPattern(mode="negative");
        } 
     */   
        
        // Make a cutout for the battery
        battery_width = 95-5;
        battery_length = 67-25;
        battery_offset_x = width-battery_width-5;
        battery_offset_y = 25;
        translate([battery_offset_x, battery_offset_y, -1]) color("blue") cube([battery_width, battery_length, thickness+2]); 
    
        translate([6+6.5+5-2-8+0.5+3, 71-10-3, -1]) {
            mkPomelloMountPattern();
        }
        
        // ESP32 Mount Pattern
        translate([100-7-5, 75-7, 10]) mkESP32MountPattern(mode="negative");

        // QWIIC board mount patterns
        //translate([100-17, 75+27, -1]) mkSparkfunGenericQWIICBoardMountPattern(mode="negative");
        //translate([100-17, 75-7, -1]) mkSparkfunGenericQWIICBoardMountPattern(mode="negative");
        
        // Camera mount
        translate([116.5, 86, 4]) rotate([0, 180, 0]) color("blue") camera_board_mount(mode="negative");

        // Spectrometer mount
        translate([102.0, 149, 2]) rotate([0, 180, 0]) color("red") mkSpecMount(mode="negative");
        
        // Sensor board (vertical)
        //translate([10.5, 130+2, -0]) rotate([0, 180, 0]) mkSensorBoardMountVertical(mode="negative");                
        //translate([10.5, 130+2-43-27, -0]) rotate([0, 180, 0]) mkSensorBoardMountVertical(mode="negative");
        
        // SPS30 
        translate([50-5, 150-16, -12.5+2]) mkSPS30Cutout(mode="negative");

        // Cutout for wires to magnetic tile
        translate([width-40, length-3, -14]) color("purple") cube([5, 4, 14]);

        // Screw holes (to magnetic tile)
        translate([width-20+3.5, length+1, -20]) rotate([90, 0, 0]) cylinder(h=4.5+1, d=2.5); // Screw hole
        translate([width-50+3.5, length+1, -20]) rotate([90, 0, 0]) cylinder(h=4.5+1, d=2.5); // Screw hole
        // Insert hole (from magnetic tile)
        translate([width-90+1.5, length+1, -5]) color("green")rotate([90, 0, 0]) cylinder(h=6+1, d=3.5); // Screw hole

        
    /*
        translate([65, 75, -1]) {
            mkZero4UMountPattern();
        }
    */
        
        // Thermal Camera
        /*
        translate([42+4, 120, -1]) {
            mkWaveshareThermalMountPattern();
        }    
        
        // Spectrometer
        translate([62, 150+3, -3.6]) {
            mkSpecMountPattern(mode="negative");
        }
        
        // Camera
        translate([60+2, 120, -3.6]) {
            mkCameraMountPattern(mode="negative");
        }
        
        // Air particle
        translate([86-1, 120, 0]) {
            mkAirParticleSensorMountPattern(mode="negative");
        }
        */
        
        // USB Hub
        translate([12.5, 30-5, -1]) {            
            translate([-2+2, -10, 0]) cube([18, 38, 10]);  // Cutout for the cable        
        }
        translate([(width/2)+15-8, 6+0.5, -0.1]) {
            rotate([0, 0, 90]) mkUSBHubMountPattern(mode="negative");      
        }  
        
        // Mount holes for the front sensor section
        // Screw holes to mount the front to the bottom plate
        /*
        front_screw_mount_dia = 4.0;
        translate([12, length+10/2, thickness/2]) rotate([90, 0, 0]) color("purple") cylinder(h=10, d=front_screw_mount_dia);
        translate([12+(15*1), length+10/2, thickness/2]) rotate([90, 0, 0]) color("purple") cylinder(h=10, d=front_screw_mount_dia);
        translate([12+(15*2), length+10/2, thickness/2]) rotate([90, 0, 0]) color("purple") cylinder(h=10, d=front_screw_mount_dia);
        translate([12+(15*3), length+10/2, thickness/2]) rotate([90, 0, 0]) color("purple") cylinder(h=10, d=front_screw_mount_dia);
        translate([12+(15*4), length+10/2, thickness/2]) rotate([90, 0, 0]) color("purple") cylinder(h=10, d=front_screw_mount_dia);
        translate([12+(15*5), length+10/2, thickness/2]) rotate([90, 0, 0]) color("purple") cylinder(h=10, d=front_screw_mount_dia);
        translate([12+(15*6), length+10/2, thickness/2]) rotate([90, 0, 0]) color("purple") cylinder(h=10, d=front_screw_mount_dia);
        translate([12+(15*7), length+10/2, thickness/2]) rotate([90, 0, 0]) color("purple") cylinder(h=10, d=front_screw_mount_dia);
        */
    
    
    }

}


//
// Main
//

// Uncomment to build the main body
main();

// Uncomment to build the back cover
//mkBackCover1();

// Uncomment to build the top of the magnetic tile holder
//translate([width, length+5, -25]) rotate([1800, 180, 0]) magneticTileHolder1Grid();

// Uncomment to build the bottom of the magnetic tile holder
//translate([width, length+5, -25]) rotate([1800, 180, 0]) magneticTileHolder1a();
