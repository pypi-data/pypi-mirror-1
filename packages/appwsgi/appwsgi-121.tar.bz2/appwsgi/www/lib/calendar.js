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
 'displayMonth'                : '',
 'displayYear'                 : '',
 'displayHour'                 : '',
 'displayMinute'               : '',
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

 'isLeapYear':function(y)
 {
  if(y%400==0||(y%4==0&&y%100!=0)) return true;
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
  var jd = day + Math.floor(((153*m)+2)/5) + (365*y) + Math.floor(y/4) - Math.floor(y/100) + Math.floor(y/400) - 32045;
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
  calendar.displayYear = this.innerHTML.replace(/[^\d]/g,'');
  document.getElementById('yearDropDown').style.display='none';
  calendar.display()
 },

 'selectMonth':function()
 {
  document.getElementById('calendar_month_txt').innerHTML = this.innerHTML
  calendar.displayMonth = this.id.replace(/[^\d]/g,'');
  document.getElementById('monthDropDown').style.display='none';
  calendar.display()
 },

 'selectHour':function()
 {
  document.getElementById('calendar_hour_txt').innerHTML = this.innerHTML
  calendar.displayHour = this.innerHTML.replace(/[^\d]/g,'');
  calendar.inputHour = parseInt(calendar.displayHour)
  document.getElementById('hourDropDown').style.display='none';
  if(calendar.activeSelectBoxHour)calendar.activeSelectBoxHour.style.color='';
  calendar.activeSelectBoxHour=this;
  this.style.color = calendar.selectBoxHighlightColor;
 },

 'selectMinute':function()
 {
  document.getElementById('calendar_minute_txt').innerHTML = this.innerHTML
  calendar.displayMinute = this.innerHTML.replace(/[^\d]/g,'');
  calendar.inputMinute = parseInt(calendar.displayMinute)
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
	if(calendar.displayYear){d.setFullYear(calendar.displayYear);}
	var startYear = d.getFullYear()/1 - 5;
	var subDiv = document.createElement('div');
	subDiv.innerHTML = '-';
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
     if(calendar.displayYear==no)
     {
      subDiv.style.color = calendar.selectBoxHighlightColor;
      calendar.activeSelectBoxYear = subDiv;
     }			
    }
	var subDiv = document.createElement('div');
	subDiv.innerHTML = '+';
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
   if(calendar.displayMonth==no)
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
     for(var no=0;no<subDivs.length;no++)subDivs[no].parentNode.removeChild(subDivs[no]);
	}		
	if(!calendar.displayHour)calendar.displayHour=0;
	var startHour = calendar.displayHour/1;	
	if(startHour>14)startHour=14;
	var subDiv = document.createElement('div');
	subDiv.innerHTML = '-';
	subDiv.onmousedown = function(){calendar.slideCalendarSelectBox(this)}
	subDiv.onmouseup = function(){clearTimeout(calendar.thread)}		
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
		if(calendar.displayHour==no)
        {
         subDiv.style.color = calendar.selectBoxHighlightColor;
         calendar.activeSelectBoxHour = subDiv;
		}			
	}
	var subDiv = document.createElement('div');
	subDiv.innerHTML = '+';
	subDiv.onmousedown = function(){calendar.slideCalendarSelectBox(this)}
	subDiv.onmouseup = function(){clearTimeout(calendar.thread);}	
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
	for(var no=0;no<60;no+=5)
    {
		if(no<10)prefix='0'; else prefix = '';
		var subDiv = document.createElement('div');
		subDiv.innerHTML = prefix + no;
		subDiv.onclick = calendar.selectMinute;		
		subDiv.id = 'minuteDiv' + prefix +  no;
        subDiv.className="selectbox"	
		div.appendChild(subDiv);
		if(calendar.displayMinute==no)
        {
		 subDiv.style.color = calendar.selectBoxHighlightColor;
		 calendar.activeSelectBoxMinute = subDiv;
		}			
	}
	return div;	
 },

 'changeSelectBoxYear':function(inputObj)
 {
  var yearItems = document.getElementById('yearDropDown').getElementsByTagName('div');
  if     (inputObj.innerHTML.indexOf('-')>=0){var startYear = yearItems[1].innerHTML/1 -1;}
  else if(inputObj.innerHTML.indexOf('+')>=0){var startYear = yearItems[1].innerHTML/1 +1;}
  else                                        var startYear = yearItems[1].innerHTML/1;
  for(var no=1;no<yearItems.length-1;no++)
  {
   yearItems[no].innerHTML = startYear+no-1;	
   yearItems[no].id = 'yearDiv' + (startYear/1+no/1-1);
   if ( (startYear/1+no/1-1) == calendar.displayYear )
   {
    yearItems[no].style.color='red'
    calendar.activeSelectBoxYear=yearItems[no]
   }
   else yearItems[no].style.color=''
  }	
 },

 'changeSelectBoxMonth':function()
 {
  for(var no=0;no<calendar.monthArray.length;no++)
  {
   var n
   if(no<10){n='0'+no}else{n=no}
   var subDiv=document.getElementById('monthDiv'+n)
   subDiv.style.color = ''
   if(calendar.displayMonth==no)
   {
    subDiv.style.color = calendar.selectBoxHighlightColor
    calendar.activeSelectBoxMonth = subDiv
   }				
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
        if ( (prefix+(startHour/1+no/1-1)) == calendar.displayHour )
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
	span.innerHTML = calendar.displayYear;
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
	span.innerHTML = calendar.monthArray[calendar.displayMonth];
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
	calendar.displayMonth = calendar.displayMonth/1;
	var d = new Date();	
	d.setFullYear(calendar.displayYear);
	d.setDate(1);
	d.setMonth(calendar.displayMonth);
	var dayStartOfMonth = d.getDay();
	if(dayStartOfMonth==0)dayStartOfMonth=7;
	dayStartOfMonth--;
	document.getElementById('calendar_year_txt').innerHTML   = calendar.displayYear;
	document.getElementById('calendar_month_txt').innerHTML  = calendar.monthArray[calendar.displayMonth];
	document.getElementById('calendar_hour_txt').innerHTML   = calendar.displayHour;
	document.getElementById('calendar_minute_txt').innerHTML = calendar.displayMinute;
	if(calendar.contentDiv.getElementsByTagName('table').length>0){calendar.contentDiv.removeChild(calendar.contentDiv.getElementsByTagName('table')[0])}
	var calTable = document.createElement('table');
	calTable.width = '100%';
	calTable.cellSpacing = '0';
	calendar.contentDiv.appendChild(calTable);
	var row = calTable.insertRow(-1);
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
	var row = calTable.insertRow(-1);
	var cell = row.insertCell(-1);
	cell.className = 'calendar_week_column';
	cell.style.backgroundColor = calendar.selectBoxRolloverBgColor;
	var week = calendar.getWeek(calendar.displayYear,calendar.displayMonth,1);
	cell.innerHTML = week;
	for(var no=0;no<dayStartOfMonth;no++)
    {
     var cell = row.insertCell(-1);
     cell.innerHTML = ' ';
	}
	var colCounter = dayStartOfMonth;
	var daysInMonth = calendar.daysInMonthArray[calendar.displayMonth];
	if(daysInMonth==28){if(calendar.isLeapYear(calendar.displayYear))daysInMonth=29;}
	for(var no=1;no<=daysInMonth;no++)
    {
		if(colCounter>0 && colCounter%7==0)
        {
         var row = calTable.insertRow(-1);
         var cell = row.insertCell(-1);
         cell.className = 'calendar_week_column';
         var week = calendar.getWeek(calendar.displayYear,calendar.displayMonth,no);
         cell.innerHTML = week;
         cell.style.backgroundColor = calendar.selectBoxRolloverBgColor;			
		}
		var cell = row.insertCell(-1);
		if(calendar.displayYear==calendar.inputYear && calendar.displayMonth == calendar.inputMonth && no==calendar.inputDay){cell.className='activeDay'}
        if (no < 10) no='0'+no
        cell.id = no
        cell.innerHTML = no
        cell.onclick = calendar.pickDate;
		colCounter++;
	}
 },
 
 'pickTodaysDate':function()
 {
  var t = new Date()
  var y = t.getFullYear()
  var m = t.getMonth()+1
  var d = t.getDate()
  var h = t.getHours()
  var i = t.getMinutes()

  calendar.displayYear   =y
  calendar.displayMonth  =m-1
  calendar.displayHour   =h
  calendar.displayMinute =i

  calendar.inputYear     =y 
  calendar.inputMonth    =m-1
  calendar.inputDay      =d
  calendar.inputHour     =h
  calendar.inputMinute   =i

  calendar.display()
 },

 'pickDate':function()
 {
  calendar.close()

  calendar.inputYear   = calendar.displayYear 
  calendar.inputMonth  = calendar.displayMonth
  calendar.inputDay    = this.id
  calendar.inputHour   = calendar.displayHour
  calendar.inputMinute = calendar.displayMinute

  calendar.changeSelectBoxYear(this)
  calendar.changeSelectBoxMonth()

  document.getElementById('calendarDiv').style.width='222px'
  document.getElementById('calendarDiv').style.height='154px'
  document.getElementById('calendarDiv').style.overflow='visible'

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
	span.innerHTML = calendar.displayHour;
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
	span.innerHTML = calendar.displayMinute;
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

 'set':function(v)
 {
  var i=v.split(/[^0-9]/gi)
  if(i)
  {
   calendar.inputYear     = i[0]
   calendar.inputMonth    = i[1]-1
   calendar.inputDay      = i[2]
   calendar.inputHour     = i[3]
   calendar.inputMinute   = i[4]
   calendar.displayYear   = i[0]
   calendar.displayMonth  = i[1]-1
   calendar.displayHour   = i[3]
   calendar.displayMinute = i[4]
  }
  calendar.changeSelectBoxYear(document.createElement('div'))
  calendar.changeSelectBoxMonth()
 },

 'get':function()
 {
  var y = calendar.inputYear 
  var m = calendar.inputMonth+1
  var d = calendar.inputDay
  var h = calendar.inputHour
  var i = calendar.inputMinute
  if (m<10) m='0'+m
  if (d<10) d='0'+d
  //if (h<10) h='0'+h
  //if (i<10) i='0'+i
  return y+"-"+m+"-"+d+" "+h+":"+i
 },

 'display':function()
 {
  if(!calendar.div) 
  {
   calendar.div = document.createElement('div')
   calendar.div.id = 'calendarDiv'
   calendar.div.style.width='100%'
   document.body.appendChild(calendar.div)
   calendar.writeTopBar()
  }
  calendar.writeContent()
  if(document.getElementById('calendarDiv').style.width!='100%'){return 0}
  calendar.close()
  var m=calendar.displayMonth+1
  var y=calendar.displayYear
  var n=m; if(m<10){m='0'+m} n++; if(n>12){n=1;y++;} if(n<10){n='0'+n}
  http.fml=function(v)
  {
   for (var i=0;i<v['rec'].length;i++)
   {
    var t=v['rec'][i][0].match(/-([^-]*?) /)[1]
    document.getElementById(t).innerHTML+='<p>'+v['rec'][i][1]+'</p>'
    document.getElementById(t).style.background='#c0c0c0'
   }
  }
  http.xml ='{"cmd":"overview",\n'
  http.xml+=' "sid":"'+session.sid+'",\n'
  http.xml+=' "gid":"",\n'
  http.xml+=' "from":"'+y+'-'+m+'-01 00:00:00.0",\n'
  http.xml+=' "to":"'+y+'-'+n+'-01 00:00:00.0"}\n'
  http.url ='../../wsgi/appointment.wsgi'
  http.req ='POST'
  http.send()
  document.getElementById('calendarDiv').style.width='100%'
  document.getElementById('calendarDiv').style.height='100%'
  document.getElementById('calendarDiv').style.overflow='auto'
 }

}
