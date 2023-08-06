// Copyright(c) gert.cuykens@gmail.com
// source = http://www.dhtmlgoodies.com/ 
// source = http://www.codeproject.com/csharp/gregorianwknum.asp
calendar=
{
 'monthArray'                  : ['January','February','March','April','May','June','July','August','September','October','November','December'],
 'monthArrayShort'             : ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'],
 'dayArray'                    : ['Mon','Tue','Wed','Thu','Fri','Sat','Sun'],
 'weekString'                  : 'Week',
 'daysInMonthArray'            : [31,28,31,30,31,30,31,31,30,31,30,31],
 'currentMonth'                : '',
 'currentYear'                 : '',
 'currentHour'                 : '',
 'currentMinute'               : '',
 'contentDiv'                  : '',
 'inputYear'                   : '',
 'inputMonth'                  : '',
 'inputDay'                    : '',
 'inputHour'                   : '',
 'inputMinute'                 : '',
 'selectBoxHighlightColor'     : '#D60808', 
 'selectBoxRolloverBgColor'    : '#E2EBED',
 'activeSelectBoxMonth'        : '',
 'activeSelectBoxYear'         : '',
 'activeSelectBoxHour'         : '',
 'activeSelectBoxMinute'       : '',
 'thread'                      : '',

 'isLeapYear':function(inputYear)
 {
    if(inputYear%400==0||(inputYear%4==0&&inputYear%100!=0)) return true;
    return false;	
 },

 'getWeek':function(year,month,day)
 {
	day = day/1;
	year = year/1;
    month = month/1 + 1;
    var a = Math.floor((14-(month))/12);
    var y = year+4800-a;
    var m = (month)+(12*a)-3;
    var jd = day + Math.floor(((153*m)+2)/5) + 
             (365*y) + Math.floor(y/4) - Math.floor(y/100) + 
             Math.floor(y/400) - 32045;
    var d4 = (jd+31741-(jd%7))%146097%36524%1461;
    var L = Math.floor(d4/1460);
    var d1 = ((d4-L)%365)+L;
    var NumberOfWeek = Math.floor(d1/7) + 1;
    return NumberOfWeek;        
 },

 'showYearDropDown':function()
 {
	if(document.getElementById('yearDropDown').style.display=='block') document.getElementById('yearDropDown').style.display='none';
    else
    {
		document.getElementById('yearDropDown').style.display='block';	
		document.getElementById('monthDropDown').style.display='none';	
		document.getElementById('hourDropDown').style.display='none';
		document.getElementById('minuteDropDown').style.display='none';	
	}		
 },

 'showMonthDropDown':function()
 {
	if(document.getElementById('monthDropDown').style.display=='block') document.getElementById('monthDropDown').style.display='none';
    else
    {
	 document.getElementById('monthDropDown').style.display='block';		
	 document.getElementById('yearDropDown').style.display='none';
	 document.getElementById('hourDropDown').style.display='none';
	 document.getElementById('minuteDropDown').style.display='none';
	}
 },

 'showHourDropDown':function()
 {
	if(document.getElementById('hourDropDown').style.display=='block') document.getElementById('hourDropDown').style.display='none';
    else
    {
		document.getElementById('hourDropDown').style.display='block';	
		document.getElementById('monthDropDown').style.display='none';	
		document.getElementById('yearDropDown').style.display='none';	
		document.getElementById('minuteDropDown').style.display='none';	
        document.getElementById('hourDropDown').style.left=document.getElementById('timeBar').offsetLeft+2+'px'
	}
   		
 },

 'showMinuteDropDown':function()
 {
	if(document.getElementById('minuteDropDown').style.display=='block') document.getElementById('minuteDropDown').style.display='none';
    else
    {
		document.getElementById('minuteDropDown').style.display='block';	
		document.getElementById('monthDropDown').style.display='none';	
		document.getElementById('yearDropDown').style.display='none';	
		document.getElementById('hourDropDown').style.display='none';
        document.getElementById('minuteDropDown').style.left=document.getElementById('timeBar').offsetLeft+37+'px'	
	}		
 },

 'selectYear':function()
 {
	document.getElementById('calendar_year_txt').innerHTML = this.innerHTML
	calendar.currentYear = this.innerHTML.replace(/[^\d]/g,'');
	document.getElementById('yearDropDown').style.display='none';
	if(calendar.activeSelectBoxYear)calendar.activeSelectBoxYear.style.color='';
	calendar.activeSelectBoxYear=this;
	this.style.color = calendar.selectBoxHighlightColor;
	calendar.writeContent();
    if (document.getElementById('calendarDiv').style.width=='100%') calendar.overview()
 },


 'selectMonth':function()
 {
	document.getElementById('calendar_month_txt').innerHTML = this.innerHTML
	calendar.currentMonth = this.id.replace(/[^\d]/g,'');
	document.getElementById('monthDropDown').style.display='none';
	for(var no=0;no<calendar.monthArray.length;no++)
    {
     var prefix = '';
     if(no/1<10)prefix='0';
     document.getElementById('monthDiv'+prefix+no).style.color='';
    }
	this.style.color = calendar.selectBoxHighlightColor;
	calendar.activeSelectBoxMonth = this;
	calendar.writeContent();
    if (document.getElementById('calendarDiv').style.width=='100%') calendar.overview()
 },

 'selectHour':function()
 {
	document.getElementById('calendar_hour_txt').innerHTML = this.innerHTML
	calendar.currentHour = this.innerHTML.replace(/[^\d]/g,'');
	document.getElementById('hourDropDown').style.display='none';
	if(calendar.activeSelectBoxHour)calendar.activeSelectBoxHour.style.color='';
	calendar.activeSelectBoxHour=this;
	this.style.color = calendar.selectBoxHighlightColor;
 },

 'selectMinute':function()
 {
	document.getElementById('calendar_minute_txt').innerHTML = this.innerHTML
	calendar.currentMinute = this.innerHTML.replace(/[^\d]/g,'');
	document.getElementById('minuteDropDown').style.display='none';
	if(calendar.activeSelectBoxMinute)calendar.activeSelectBoxMinute.style.color='';
	calendar.activeSelectBoxMinute=this;
	this.style.color = calendar.selectBoxHighlightColor;
    
 },

 'createYearDiv':function()
 {
	if(!document.getElementById('yearDropDown'))
    {
		var div = document.createElement('div');
		div.className='monthYearPicker';
	}
    else
    {
		var div = document.getElementById('yearDropDown');
		var subDivs = div.getElementsByTagName('div');
		for(var no=0;no<subDivs.length;no++) subDivs[no].parentNode.removeChild(subDivs[no]);
	}	
	var d = new Date();
	if(calendar.currentYear){d.setFullYear(calendar.currentYear);}
	var startYear = d.getFullYear()/1 - 5;
	var subDiv = document.createElement('div');
	subDiv.innerHTML = '&nbsp;&nbsp;- ';
	subDiv.onmousedown = function(){calendar.slideCalendarSelectBox(this)}
	subDiv.onmouseup = function(){clearTimeout(calendar.thread);}
	div.appendChild(subDiv);
	for(var no=startYear;no<(startYear+10);no++)
    {
		var subDiv = document.createElement('div');
		subDiv.innerHTML = no;
		subDiv.onclick = calendar.selectYear;	
		subDiv.id = 'yearDiv' + no;
        subDiv.className="selectbox"		
		div.appendChild(subDiv);
		if(calendar.currentYear==no)
        {
			subDiv.style.color = calendar.selectBoxHighlightColor;
			calendar.activeSelectBoxYear = subDiv;
		}			
	}
	var subDiv = document.createElement('div');
	subDiv.innerHTML = '&nbsp;&nbsp;+ ';
	subDiv.onmousedown = function(){calendar.slideCalendarSelectBox(this)}
	subDiv.onmouseup = function(){clearTimeout(calendar.thread);}
	div.appendChild(subDiv);		
	return div;
 },

 'createMonthDiv':function()
 {
	var div = document.createElement('div');
	div.className='monthYearPicker';
	div.id = 'monthPicker';
	for(var no=0;no<calendar.monthArray.length;no++)
    {
		var subDiv = document.createElement('div');
		subDiv.innerHTML = calendar.monthArray[no];
		subDiv.onclick = calendar.selectMonth;
        var prefix='';
        if(no/1<10)prefix='0';
		subDiv.id = 'monthDiv' +prefix+ no;
        subDiv.className="selectbox"
		subDiv.style.width = '56px';
		div.appendChild(subDiv);
		if(calendar.currentMonth==no)
        {
			subDiv.style.color = calendar.selectBoxHighlightColor;
			calendar.activeSelectBoxMonth = subDiv;
		}				
	}	
	return div;
 },

 'createHourDiv':function()
 {
	if(!document.getElementById('hourDropDown'))
    {
		var div = document.createElement('div');
		div.className='monthYearPicker';
	}
    else
    {
		var div = document.getElementById('hourDropDown');
		var subDivs = div.getElementsByTagName('div');
		for(var no=0;no<subDivs.length;no++) subDivs[no].parentNode.removeChild(subDivs[no]);
	}		
	if(!calendar.currentHour)calendar.currentHour=0;
	var startHour = calendar.currentHour/1;	
	if(startHour>14)startHour=14;
	var subDiv = document.createElement('div');
	subDiv.innerHTML = '&nbsp;&nbsp;- ';
	subDiv.onmousedown = function(){calendar.slideCalendarSelectBox(this)}
	subDiv.onmouseup =  function(){clearTimeout(calendar.thread)}		
	div.appendChild(subDiv);
	for(var no=startHour;no<startHour+10;no++)
    {
		var prefix = '';
		if (no/1<10) prefix='0';
		var subDiv = document.createElement('div');
		subDiv.innerHTML = prefix + no;	
		subDiv.onclick = calendar.selectHour;		
		subDiv.id = 'hourDiv' + prefix + no;
        subDiv.className="selectbox"	
		div.appendChild(subDiv);
		if(calendar.currentHour==no)
        {
			subDiv.style.color = calendar.selectBoxHighlightColor;
			calendar.activeSelectBoxHour = subDiv;
		}			
	}
	var subDiv = document.createElement('div');
	subDiv.innerHTML = '&nbsp;&nbsp;+ ';
	subDiv.onmousedown = function(){calendar.slideCalendarSelectBox(this)}
	subDiv.onmouseup =  function(){clearTimeout(calendar.thread);}	
	div.appendChild(subDiv);
	return div;	
 },

 'createMinuteDiv':function()
 {
	if(!document.getElementById('minuteDropDown'))
    {
		var div = document.createElement('div');
		div.className='monthYearPicker';
	}
    else
    {
		var div = document.getElementById('minuteDropDown');
		var subDivs = div.getElementsByTagName('div');
		for(var no=0;no<subDivs.length;no++) subDivs[no].parentNode.removeChild(subDivs[no]);	
	}		
	var prefix = '';
	for(var no=0;no<60;no+=15)
    {
		if(no<10)prefix='0'; else prefix = '';
		var subDiv = document.createElement('div');
		subDiv.innerHTML = prefix + no;
		subDiv.onclick = calendar.selectMinute;		
		subDiv.id = 'minuteDiv' + prefix +  no;
        subDiv.className="selectbox"	
		div.appendChild(subDiv);
		if(calendar.currentMinute==no)
        {
			subDiv.style.color = calendar.selectBoxHighlightColor;
			calendar.activeSelectBoxMinute = subDiv;
		}			
	}
	return div;	
 },

 'changeSelectBoxYear':function(inputObj)
 {
	var yearItems = inputObj.parentNode.getElementsByTagName('div');	
    if(inputObj.innerHTML.indexOf('-')>=0){var startYear = yearItems[1].innerHTML/1 -1;}
    else{var startYear = yearItems[1].innerHTML/1 +1;}
	for(var no=1;no<yearItems.length-1;no++)
    {
		yearItems[no].innerHTML = startYear+no-1;	
		yearItems[no].id = 'yearDiv' + (startYear/1+no/1-1);
        if ( (startYear/1+no/1-1) == calendar.currentYear )
        {
         yearItems[no].style.color='red'
         calendar.activeSelectBoxYear=yearItems[no]
        }
        else yearItems[no].style.color=''
	}	
 },

 'changeSelectBoxHour':function(inputObj)
 {
	var hourItems = inputObj.parentNode.getElementsByTagName('div');
	if(inputObj.innerHTML.indexOf('-')>=0)
    {
		var startHour = hourItems[1].innerHTML/1 -1;
		if(startHour<0) startHour=0;
	}
    else
    {
		var startHour = hourItems[1].innerHTML/1 +1;
		if(startHour>14)startHour = 14;		
	}

	var prefix = '';
	for(var no=1;no<hourItems.length-1;no++)
    {
		if((startHour/1 + no/1) < 11) prefix = '0'; 
        else prefix = '';
		hourItems[no].innerHTML = prefix + (startHour+no-1);
		hourItems[no].id = 'hourDiv' +prefix+(startHour/1+no/1-1);
        if ( (prefix+(startHour/1+no/1-1)) == calendar.currentHour )
        {
         hourItems[no].style.color='red'
         calendar.activeSelectBoxHour=hourItems[no]
        }
        else hourItems[no].style.color=''
	}
 },

 'slideCalendarSelectBox':function(obj)
 {
  if (obj.parentNode.id=='hourDropDown') calendar.changeSelectBoxHour(obj);	
  if (obj.parentNode.id=='yearDropDown') calendar.changeSelectBoxYear(obj);
  calendar.thread=setTimeout(function(){calendar.slideCalendarSelectBox(obj)},100);
 },

 'close':function()
 {
	document.getElementById('yearDropDown').style.display='none';
	document.getElementById('monthDropDown').style.display='none';
	document.getElementById('hourDropDown').style.display='none';
	document.getElementById('minuteDropDown').style.display='none';
 },

 'writeTopBar':function()
 {
	var topBar = document.createElement('div');
	topBar.className = 'topBar';
	topBar.id = 'topBar';
	calendar.div.appendChild(topBar);

	var yearDiv = document.createElement('div');
	yearDiv.onclick = calendar.showYearDropDown;
	var span = document.createElement('span');	
	span.innerHTML = calendar.currentYear;
	span.id = 'calendar_year_txt';
	yearDiv.appendChild(span);
	topBar.appendChild(yearDiv);
	yearDiv.className = 'selectBox';
	var yearPicker = calendar.createYearDiv();
	yearPicker.style.left = '3px';
	yearPicker.style.top = '25px';
	yearPicker.style.width = '27px';
	yearPicker.id = 'yearDropDown';
	calendar.div.appendChild(yearPicker);

	var monthDiv = document.createElement('div');
	monthDiv.id = 'monthSelect';
	monthDiv.onclick = calendar.showMonthDropDown;
	var span = document.createElement('span');	
	span.innerHTML = calendar.monthArray[calendar.currentMonth];
    span.id = 'calendar_month_txt';
	monthDiv.appendChild(span);
	monthDiv.className = 'selectBox';
	topBar.appendChild(monthDiv);
	var monthPicker = calendar.createMonthDiv();
	monthPicker.style.left = '33px';
	monthPicker.style.top = '25px';
	monthPicker.style.width ='73px';
	monthPicker.id = 'monthDropDown';
	calendar.div.appendChild(monthPicker);

    var span = document.createElement('span');
    span.innerHTML = 'guest';
    span.id = 'view';
    span.onclick = function(){if(this.innerHTML=='guest')this.innerHTML='admin'; else this.innerHTML='guest';}
    topBar.appendChild(span);

    var timeDiv = calendar.writeTimeBar();
    topBar.appendChild(timeDiv);
 },

 'writeContent':function()
 {
	if(!calendar.contentDiv)
    {
		calendar.contentDiv = document.createElement('div');
		calendar.div.appendChild(calendar.contentDiv);
	}
	calendar.currentMonth = calendar.currentMonth/1;
	var d = new Date();	
	d.setFullYear(calendar.currentYear);
	d.setDate(1);
	d.setMonth(calendar.currentMonth);
	var dayStartOfMonth = d.getDay();
	if(dayStartOfMonth==0)dayStartOfMonth=7;
	dayStartOfMonth--;
	document.getElementById('calendar_year_txt').innerHTML = calendar.currentYear;
	document.getElementById('calendar_month_txt').innerHTML = calendar.monthArray[calendar.currentMonth];
	document.getElementById('calendar_hour_txt').innerHTML = calendar.currentHour;
	document.getElementById('calendar_minute_txt').innerHTML = calendar.currentMinute;
	var existingTable = calendar.contentDiv.getElementsByTagName('TABLE');
	if(existingTable.length>0){calendar.contentDiv.removeChild(existingTable[0]);}
	var calTable = document.createElement('TABLE');
	calTable.width = '100%';
	calTable.cellSpacing = '0';
	calendar.contentDiv.appendChild(calTable);
	var calTBody = document.createElement('TBODY');
	calTable.appendChild(calTBody);
	var row = calTBody.insertRow(-1);
	row.className = 'calendar_week_row';
	var cell = row.insertCell(-1);
	cell.innerHTML = calendar.weekString;
	cell.className = 'calendar_week_column';
	cell.style.backgroundColor = calendar.selectBoxRolloverBgColor;
	for(var no=0;no<calendar.dayArray.length;no++)
    {
		var cell = row.insertCell(-1);
		cell.innerHTML = calendar.dayArray[no]; 
	}
	var row = calTBody.insertRow(-1);
	var cell = row.insertCell(-1);
	cell.className = 'calendar_week_column';
	cell.style.backgroundColor = calendar.selectBoxRolloverBgColor;
	var week = calendar.getWeek(calendar.currentYear,calendar.currentMonth,1);
	cell.innerHTML = week;
	for(var no=0;no<dayStartOfMonth;no++)
    {
		var cell = row.insertCell(-1);
		cell.innerHTML = '&nbsp;';
	}
	var colCounter = dayStartOfMonth;
	var daysInMonth = calendar.daysInMonthArray[calendar.currentMonth];
	if(daysInMonth==28){if(calendar.isLeapYear(calendar.currentYear))daysInMonth=29;}
	for(var no=1;no<=daysInMonth;no++)
    {
		if(colCounter>0 && colCounter%7==0)
        {
			var row = calTBody.insertRow(-1);
			var cell = row.insertCell(-1);
			cell.className = 'calendar_week_column';
			var week = calendar.getWeek(calendar.currentYear,calendar.currentMonth,no);
			cell.innerHTML = week;
			cell.style.backgroundColor = calendar.selectBoxRolloverBgColor;			
		}
		var cell = row.insertCell(-1);
		if(calendar.currentYear==calendar.inputYear && calendar.currentMonth == calendar.inputMonth && no==calendar.inputDay){cell.className='activeDay'}
        if (no < 10) no='0'+no
        cell.id = no
        cell.innerHTML = no
        cell.onclick = calendar.pickDate;
		colCounter++;
	}
 },
 
 'overview':function()
 {
  calendar.close()
  http.fml=function(v)
  {
   var i=0;
   for (i=0;i<v.rec.length;i++)
   {
    t=v['rec'][i][0].match(/-([^-]*?) /)[1]
    document.getElementById(t).innerHTML+='<p>'+v['rec'][i][1]+'</p>'
    document.getElementById(t).style.background='#c0c0c0'
   }
  }
  http.xml ='{"cmd":"overview",\n'
  http.xml+=' "gid":"'+document.getElementById('view').innerHTML+'",\n'
  var m=calendar.currentMonth+1
  var y=calendar.currentYear
  var n=m
  if (m<10) m='0'+m
  http.xml+=' "from":"'+y+'-'+m+'-01 00:00:00.0",\n'
  n++;if(n>12){n=1;y++;}
  if (n<10) n='0'+n
  http.xml+=' "to":"'+y+'-'+n+'-01 00:00:00.0"}\n'
  http.url ='../../wsgi/appointment.wsgi'
  http.send()
  document.getElementById('calendarDiv').style.width='100%'
  document.getElementById('calendarDiv').style.height='100%'
  document.getElementById('calendarDiv').style.overflow='auto'
 },

 'pickTodaysDate':function()
 {
  var t = new Date()
  var y = t.getFullYear()
  var m = t.getMonth()+1
  var d = t.getDate()
  var h = t.getHours()
  var i = t.getMinutes()

  calendar.currentMonth=m-1
  calendar.currentYear=y
  calendar.currentHour=h
  calendar.currentMinute=i

  if (m<10) m='0'+m
  if (d<10) d='0'+d
  if (h<10) h='0'+h
  if (i<10) i='0'+i

  document.getElementById('calendar').value=y+"-"+m+"-"+d+" "+h+":"+i

  calendar.display()
 },

 'pickDate':function()
 {
  calendar.close()

  var y = calendar.currentYear 
  var m = calendar.currentMonth+1
  var d = this.id
  var h = calendar.currentHour
  var i = calendar.currentMinute

  if (m<10) m='0'+m

  document.getElementById('calendarDiv').style.width='222px'
  document.getElementById('calendarDiv').style.height='154px'
  document.getElementById('calendarDiv').style.overflow='visible'
  document.getElementById('calendar').value=y+"-"+m+"-"+d+" "+h+":"+i
  calendar.display()
 },

 'writeTimeBar':function()
 {
	var timeBar = document.createElement('div');
	timeBar.id = 'timeBar';
	timeBar.className = 'timeBar';	

	var hourDiv = document.createElement('div');
	hourDiv.onclick = calendar.showHourDropDown;    
	hourDiv.style.width = '30px';

	var span = document.createElement('span');
	span.innerHTML = calendar.currentHour;
	span.id = 'calendar_hour_txt';
	hourDiv.appendChild(span);
	timeBar.appendChild(hourDiv);

	hourDiv.className = 'selectBoxTime';
	var hourPicker = calendar.createHourDiv();
	hourPicker.id = 'hourDropDown';
    hourPicker.style.width = '30px';
	calendar.div.appendChild(hourPicker);

	var minuteDiv = document.createElement('div');
	minuteDiv.onclick = calendar.showMinuteDropDown;
	minuteDiv.style.width = '30px';

	var span = document.createElement('span');		
	span.innerHTML = calendar.currentMinute;
	span.id = 'calendar_minute_txt';
	minuteDiv.appendChild(span);
	timeBar.appendChild(minuteDiv);
	minuteDiv.className = 'selectBoxTime';

	var minutePicker = calendar.createMinuteDiv();
	minutePicker.style.width = '35px';
	minutePicker.id = 'minuteDropDown';
    minutePicker.style.width = '30px';
	calendar.div.appendChild(minutePicker);

	return timeBar;
 },
	
 'initCalendar':function()
 {
	calendar.div = document.createElement('div')	
	calendar.div.id = 'calendarDiv'
    calendar.div.style.width='100%'
	document.body.appendChild(calendar.div)
	calendar.writeTopBar()
 },

 'display':function()
 {
    if (!calendar.div) calendar.initCalendar()

    var items=document.getElementById('calendar').value.split(/[^0-9]/gi)
    if(items)
    {
     calendar.inputYear     = items[0]
     calendar.inputMonth    = items[1]-1
     calendar.inputDay      = items[2]
     calendar.inputHour     = items[3]
     calendar.inputMinute   = items[4]
     calendar.currentYear   = items[0]
     calendar.currentMonth  = items[1]-1
     calendar.currentDay    = items[2]
     calendar.currentHour   = items[3]
     calendar.currentMinute = items[4]
    }
  
    calendar.writeContent()

    if (document.getElementById('calendarDiv').style.width=='100%') calendar.overview()

  }

}

