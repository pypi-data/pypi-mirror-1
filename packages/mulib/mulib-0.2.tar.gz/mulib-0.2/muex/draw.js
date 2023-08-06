

function UUID() {
	// not really a uuid
	var epoch = new Date();
	return epoch.toLocaleString() + '(' + Math.random() + ')';
}


function find_rect(shape_info) {
	var min_x = shape_info.start_x < shape_info.end_x ? shape_info.start_x : shape_info.end_x;
	var min_y = shape_info.start_y < shape_info.end_y ? shape_info.start_y : shape_info.end_y;
	var max_x = shape_info.start_x > shape_info.end_x ? shape_info.start_x : shape_info.end_x;
	var max_y = shape_info.start_y > shape_info.end_y ? shape_info.start_y : shape_info.end_y;
	return [min_x, min_y, max_x - min_x, max_y - min_y];
}


function roundedRect(ctx,x,y,width,height,radius){
  ctx.beginPath();
  ctx.moveTo(x,y+radius);
  ctx.lineTo(x,y+height-radius);
  ctx.quadraticCurveTo(x,y+height,x+radius,y+height);
  ctx.lineTo(x+width-radius,y+height);
  ctx.quadraticCurveTo(x+width,y+height,x+width,y+height-radius);
  ctx.lineTo(x+width,y+radius);
  ctx.quadraticCurveTo(x+width,y,x+width-radius,y);
  ctx.lineTo(x+radius,y);
  ctx.quadraticCurveTo(x,y,x,y+radius);
  ctx.stroke();
  ctx.closePath();
}


function observe_shape(event, path, shape_info) {
	var canvas = document.getElementById('the-canvas');
	var ctx = canvas.getContext('2d');
	if (shape_info.stroke_color) {
	   ctx.strokeStyle = shape_info.stroke_color;
	}
	if (shape_info.shape == 'line') {
		ctx.beginPath()
		ctx.moveTo(shape_info.start_x, shape_info.start_y);
		ctx.lineTo(shape_info.end_x, shape_info.end_y);
		ctx.stroke();
        ctx.closePath();
	} else if (shape_info.shape == 'rect') {
		var box = find_rect(shape_info);
		ctx.strokeRect(box[0], box[1], box[2], box[3]);
	} else if (shape_info.shape == 'rrect') {
		var box = find_rect(shape_info);
		roundedRect(ctx, box[0], box[1], box[2], box[3], 10);
	} else if (shape_info.shape == 'draw') {
		ctx.beginPath()
		ctx.moveTo(shape_info.start_x, shape_info.start_y);
		for (var i = 0; i < shape_info.draw_points.length; i++) {
			ctx.lineTo(shape_info.draw_points[i][0], shape_info.draw_points[i][1]);
		}
		ctx.lineTo(shape_info.end_x, shape_info.end_y);
		ctx.stroke();
        ctx.closePath();
	}
	console.log('observe shape', shape_info);
};


var start_x;
var start_y;
var draw_points = [];
var draw_ctx;
var current_tool = 'draw';
var current_tool_node;


function drawmousemove(evt) {
	draw_points.push([evt.pageX, evt.pageY]);
	draw_ctx.lineTo(evt.pageX, evt.pageY);
	draw_ctx.stroke();
    draw_ctx.closePath();
	var canvas = document.getElementById('the-canvas');
	draw_ctx = canvas.getContext('2d');
    draw_ctx.strokeStyle = getElement('current-color').style.backgroundColor;
	draw_ctx.moveTo(evt.pageX, evt.pageY);
}


function mousedown(evt) {
	start_x = evt.pageX;
	start_y = evt.pageY;
	if (current_tool == 'draw') {
		evt.target.onmousemove = drawmousemove;
		var canvas = document.getElementById('the-canvas');
		draw_ctx = canvas.getContext('2d');
        draw_ctx.strokeStyle = getElement('current-color').style.backgroundColor;
		draw_ctx.moveTo(start_x, start_y);
	}
}


function mouseup(evt) {
	var shape = {
	   'shape': current_tool,
	   'stroke_color': getElement('current-color').style.backgroundColor,
	   'start_x': start_x, 'start_y': start_y,
	   'end_x': evt.pageX, 'end_y': evt.pageY};
	if (current_tool == 'draw') {
		evt.target.onmousemove = null;
		shape['draw_points'] = draw_points;
		draw_points = [];
		draw_ctx.stroke();
		draw_ctx.closePath();
		draw_ctx = null;
	}
	// make up a new random child url for the new shape
    doXHR(UUID(), {
            'method': 'PUT',
            'headers': {'Content-type': 'application/json'},
            'sendContent': serializeJSON(shape)}
        );
}


function toolclick(evt) {
	removeElementClass(current_tool_node, 'tool-selected');
	current_tool = evt.target.title;
	current_tool_node = evt.target;
	addElementClass(evt.target, 'tool-selected');
	console.log('toolclick', evt, evt.target, evt.target.title);
}


function make_change_color(color_string) {
    return function() {
        getElement('current-color').style.backgroundColor = color_string;
    }
}

function main() {
	current_tool_node = TD({'class': 'tool tool-selected', 'title': 'draw', 'onclick': toolclick}, " ");
	var tools = [
		TR({'class': 'tools'},
			current_tool_node,
			TD({'class': 'tool', 'title': 'line', 'onclick': toolclick}), " "),
		TR({'class': 'tools'},
			TD({'class': 'tool', 'title': 'rect', 'onclick': toolclick}, " "),
			TD({'class': 'tool', 'title': 'rrect', 'onclick': toolclick}, " "))

		];

    var colors = [];
    var current_color_row = [];
    for (var r = 0; r < 16; r++) {
        for (var g = 0; g < 16; g++) {
            for (var b = 0; b < 16; b++) {
                var color_string = '#' + r.toString(16) + r.toString(16) + g.toString(16) + g.toString(16) + b.toString(16) + b.toString(16);
                var img = IMG({'class': 'color',
                        'src': 'http://soundfarmer.com/2x2-blank.gif',
                        'title': color_string,
                        'onmousedown': make_change_color(color_string)});
                img.style.backgroundColor = color_string;
                current_color_row.push(img);
                if (current_color_row.length == 256) {
                    colors.push(DIV({'class': 'color-row'}, current_color_row));
                    current_color_row = [];                
                }
            }
        }
    }

  	replaceChildNodes('contents',
		CANVAS({'id': 'the-canvas', 'height': 1000, 'width': 1000, 'onmousedown': mousedown, 'onmouseup': mouseup}),
  		TABLE({'id': 'toolbox'}, tools),
  		DIV({'id': 'colors'}, IMG({'id': 'current-color', 'src': 'http://soundfarmer.com/2x2-blank.gif', 'style': 'height: 32px; width: 32px; float: left; background-color: black;'}), colors)
	);
    
	// "draw" sqiggle
	var canvas = document.getElementById('the-canvas');
	var ctx = canvas.getContext('2d');
	ctx.beginPath()
	ctx.moveTo(9, 14);
	ctx.lineTo(18, 14);
	ctx.lineTo(18, 28);
	ctx.lineTo(28, 27);
	ctx.stroke();

	// line
	ctx = canvas.getContext('2d');
	ctx.beginPath()
	ctx.moveTo(40, 4);
	ctx.lineTo(68, 30);
	ctx.stroke();

	observe_shape(null, null, {'shape': 'rect', 'start_x': 4, 'start_y': 36, 'end_x': 32, 'end_y': 62});
	observe_shape(null, null, {'shape': 'rrect', 'start_x': 40, 'start_y': 36, 'end_x': 68, 'end_y': 62});
	

	observe('*', observe_shape);
}

